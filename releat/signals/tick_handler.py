"""Gets and updates tick data.

Pulls data from apis/mt5.py

#TODO when we have more trading platform integrations,
abstract the api into a general tick data api

#TODO consider using multiprocessing or threading
and manager object for tick data to pull data
in parallel

Each rl_agent holds a copy of the tick data - should data be pushed into redis
and then each rl_agent pulls data from redis to do inference?

"""
from __future__ import annotations

from datetime import datetime
from datetime import timedelta

import pandas as pd
import pytz
import requests

from releat.data.utils import update_tick_data
from releat.gym_env.action_processor import build_action_map
from releat.gym_env.action_processor import build_pos_arrs
from releat.utils.configs.config_builder import load_config
from releat.utils.configs.constants import mt5_api_port_map
from releat.utils.configs.constants import mt5_creds


class TickHandler:
    """Tick data handler."""

    def __init__(self, agent_version, symbol="general"):
        """Init.

        Args:
            agent_version (str):
                i.e. 't00001'
            symbol (str):
                this determines which ports to look for when pulling data. TODO clean
                up logic for this - possible a process for each symbol / broker
                combination

        """
        self.tick_data = None

        # load config
        self.config = load_config(agent_version, enrich_feat_spec=True, is_training=False)

        # action map - array where each row corresponds with an index in
        # the rl agents prediction. each column describes the action, i.e. long/short
        # open/close etc.
        self.action_map = build_action_map(self.config.trader)

        # list of all symbols used in agent
        self.symbols = list(self.config.symbol_info_index.keys())

        # initialise gym representation of positions
        self.gym_portfolio = build_pos_arrs(self.config.trader)
        self.gym_portfolio_hedge = build_pos_arrs(self.config.trader)

        # TODO improve how we pass through which api to start
        # individual apis per symbol?
        self.mt5_config = mt5_creds[self.config.broker]["demo"][0]
        self.port = mt5_api_port_map[self.config.broker][symbol]
        self.data_api = f"http://127.0.0.1:{self.port}"
        _ = requests.post(f"{self.data_api}/init", json=self.mt5_config)

    def init_tick_data(self, dt1, hour_delta=72):
        """Initialise tick data.

        Download tick data from MT5
        #TODO switch dt1 to int? faster but harder to read
        #TODO dynamically generate how much data to hold in memory

        Args:
            dt1 (str):
                datetime in the format "%Y-%m-%d %H:%M:%S.%f"
            hour_delta (int):
                number of hours of data to pull - generally only pull what is needed
                by the longest feature.

        """
        self.tick_data = {}

        # calculate start and end time
        dt1 = datetime.strptime(dt1, "%Y-%m-%d %H:%M:%S.%f")
        dt1 = pytz.utc.localize(dt1)
        dt0 = dt1 - timedelta(hours=hour_delta)

        # download data for each trading instrument
        for symbol in self.symbols:
            payload = {
                "symbol": symbol,
                "dt0": dt0.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "dt1": dt1.strftime("%Y-%m-%d %H:%M:%S.%f"),
            }
            df = requests.get(
                f"{self.data_api}/get_tick_data",
                json=payload,
                timeout=120,
            ).json()
            df = pd.DataFrame(df)[
                ["ask", "bid", "flags", "last", "time_msc", "volume", "volume_real"]
            ]
            df["time_msc"] = pd.to_datetime(df["time_msc"], unit="ms")
            self.tick_data[symbol] = df
        # return self.tick_data

    def update_tick_data(self, dt1):
        """Update tick data.

        Download tick data delta between existing data and new datetime.

        Args:
            dt1 (str):
                new datetime for pulling data in the format "%Y-%m-%d %H:%M:%S.%f"

        """
        new_data = {}
        dt0s = {}
        for symbol in self.symbols:
            old_df = self.tick_data[f"{symbol}"]
            dt0 = old_df["time_msc"].iloc[-1]
            dt0s[symbol] = dt0
            dt0 = dt0.replace(microsecond=0)

            payload = {
                "symbol": symbol,
                "dt0": dt0.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "dt1": dt1,
            }
            df = requests.get(f"{self.data_api}/get_tick_data", json=payload).json()
            df = pd.DataFrame(df)[
                ["ask", "bid", "flags", "last", "time_msc", "volume", "volume_real"]
            ]
            df["time_msc"] = pd.to_datetime(df["time_msc"], unit="ms")

            df = df[df["time_msc"] >= pd.to_datetime(dt0)]
            new_data[symbol] = df
        self.tick_data = update_tick_data(self.symbols, self.tick_data, new_data)

        self.check_data = {}
        for symbol in self.symbols:
            df = self.tick_data[symbol]
            idx = df[df["time_msc"] == dt0s[symbol]].index.tolist()[0]
            idx -= 10
            self.check_data[symbol] = self.tick_data[symbol].loc[idx:]

        # return self.tick_data

    def check_tick_data(self):
        """Check updated tick data.

        Check that tick data is appended correctly. This is to catch edge cases
        where data may have been pulled incorrectly. For examples microsecond are
        ignored or there might be increased latency, leading to duplicate
        or missing data.

        """
        for symbol in self.symbols:
            # updated df
            udf = self.check_data[symbol]

            # get data from MT5 that spans the previous to new datetime range
            dt0 = udf["time_msc"].iloc[0]
            dt1 = udf["time_msc"].iloc[-1]
            payload = {
                "symbol": symbol,
                "dt0": dt0.strftime("%Y-%m-%d %H:%M:%S.%f"),
                "dt1": dt1.strftime("%Y-%m-%d %H:%M:%S.%f"),
            }
            df = requests.get(f"{self.data_api}/get_tick_data", json=payload).json()
            df = pd.DataFrame(df)[
                ["ask", "bid", "flags", "last", "time_msc", "volume", "volume_real"]
            ]
            df["time_msc"] = pd.to_datetime(df["time_msc"], unit="ms")

            # ignore leading and trailing records de to microseconds
            df = df[df["time_msc"] > pd.to_datetime(dt0)]
            df = df[df["time_msc"] < pd.to_datetime(dt1)]
            df.reset_index(drop=True, inplace=True)

            udf = udf[udf["time_msc"] > pd.to_datetime(dt0)]
            udf = udf[udf["time_msc"] < pd.to_datetime(dt1)]
            udf.reset_index(drop=True, inplace=True)

            # assert that the concatenated ticks are the same as the downloaded ticks
            if not pd.testing.assert_frame_equal(udf, df):
                dt0 = dt0.strftime("%Y-%m-%d %H:%M:%S.%f")
                dt1 = dt1.strftime("%Y-%m-%d %H:%M:%S.%f")
                print(f"Error data append error: {dt0} - {dt1}")
