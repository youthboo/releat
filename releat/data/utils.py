"""Data utils.

Random function that need to find a better place to belong in

"""
from __future__ import annotations

from copy import deepcopy
from time import sleep

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import polars as pl
import requests
import statsmodels.api as sm
from dateutil.relativedelta import relativedelta
from tqdm import tqdm

from releat.utils.configs.constants import mt5_api_port_map
from releat.utils.logging import get_logger
from releat.workflows.service_manager import start_mt5_api

logger = get_logger(__name__)


def plot_hist_and_qq(arr, title, fname):
    """Plot hist and qq.

    For feature and transform config calculation. Used to check that after transforms
    data is normally distributed

    Args:
        arr (np.array)
        title (str)
        fname (str)

    Returns:
        None

    """
    df = pd.DataFrame(deepcopy(arr))
    for col in df.columns:
        fig, axes = plt.subplots(nrows=1, ncols=2)
        ax1, ax2 = axes.flatten()

        tmp = df[col].copy()

        a = tmp > 1
        tmp.loc[a] = 1 + (tmp - 1) / 2
        a = tmp > 2
        tmp.loc[a] = 2 + (tmp - 2) / 2

        a = tmp < -1
        tmp.loc[a] = -1 + (tmp + 1) / 2
        a = tmp < -2
        tmp.loc[a] = -2 + (tmp + 2) / 2

        tmp = tmp.clip(-3, 3)

        df[col] = tmp

        ax2 = tmp.hist(bins=20)
        ax2.set_title(f"{title}: {col}")
        sm.qqplot(tmp, line="45", ax=ax1)
        plt.savefig(f"{fname}.feat.{col}.png", format="png")
        plt.close()


def get_records_in_aerospike(config, client):
    """Get records in aerospike.

    Counts number of rows in aerospike table

    #TODO make it work if multiple version exist in database

    Args:
        data_config (dict)
        client (obj)
            aerospike client

    Returns:
        int

    """
    # save to static file because the windows / wine process cannot access Aerospike
    max_data_ind = client.info("sets")
    # get the record for the first namespace
    max_data_ind = max_data_ind[list(max_data_ind.keys())[0]][1]
    # filter to the correct set when there are multiple sets
    max_data_ind = max_data_ind.split("set=")
    # filter out short keys
    max_data_ind = [x for x in max_data_ind if len(x) > 6]
    # filter to correct version
    max_data_ind = [x for x in max_data_ind if x[:7] == f"{config.agent_version}:"]
    # if running for first time, i.e. building data, array will be empty
    if len(max_data_ind) > 0:
        max_data_ind = max_data_ind[0]
        # get number of objects
        max_data_ind = int(max_data_ind.split(":")[1].split("=")[-1]) - 1
        return max_data_ind
    else:
        return 0


def get_feature_dir(config, feat_group_ind, feat_ind):
    """Get feature dir.

    Gets location of where each raw and scaled feature is stored.

    Args:
        config (pydantic.BaseModel):
            as defined in 'agent_config.py'
        feat_group_ind (int):
            index of feature group
        feat_ind (int):
            index of feature within its feature group

    Returns:
        str:
            path
    """
    feat_group = config.features[feat_group_ind]
    fc = feat_group.simple_features[feat_ind]
    feature_dir = (
        f"{config.paths.feature_dir}"
        f"/{feat_group.index}_{feat_group.timeframe}"
        f"/{fc.index}_{fc.name}"
    )
    return feature_dir


def split_timeframe(timeframe):
    """Split timeframe.

    #TODO make it work for pandas and polars and transalte into a common format
    #TODO make it work for float becuase polars allows for float timeframes

    Separates timeframe so we can perform time operations

    Args:
        timeframe (str):
            for example 10s or 1h

    Returns:
        int
            integer value that applies to the unit of time
        str
            unit of time as a string

    """
    num = int("".join([s for s in timeframe if s.isdigit()]))
    unit = "".join([s for s in timeframe if not s.isdigit()])
    return num, unit


def search_aerospike_for_dt(config, client, dt, start_val=None):
    """Search aerospike for date.

    When uploading data to a table that already exists, find the index that
    corresponds to the specified datetime, dt

    Args:
        config (pydantic.BaseModels):
            as defined in 'agent_config.py'
        client (aerospike.Client):
            client for downloading and inserting records
        dt (pd.DateTime):
            each record is read and compared to this datetime
        start_val (int):
            the table index at which the scanning start

    Returns:
        int
            table index for dt, the input datetime

    """
    max_data_ind = get_records_in_aerospike(config, client)
    if start_val is not None:
        max_data_ind = min(start_val, max_data_ind)
    if max_data_ind == 0:
        return 0

    ind_offset = None
    for i in tqdm(np.arange(max_data_ind, -1, -1)):
        key = (
            config.aerospike.namespace,
            config.aerospike.set_name,
            int(i),
        )
        try:
            _, _, bins = client.get(key)
        except Exception as e:
            logger.critical(str(repr(e)))
            bins = {}
        if "date" in bins:
            if dt == bins["date"]:
                ind_offset = i
                break

    return ind_offset


def tick_list_to_polars_df(df):
    """List of polars for tick data."""
    df = pl.DataFrame(df)
    for col in df.columns:
        if df[col].dtype == pl.Utf8:
            df = df.with_columns(
                pl.col(col).str.to_datetime().cast(pl.Datetime(time_unit="ns")),
            )
    return df


def tick_polars_df_to_list(df):
    """Polars to list for tick data."""
    df = df.to_pandas()
    for col in df.columns:
        # hacky method of checking whether column is of datetime64[ns]
        if df[col].dtype.str[1] == "M":
            df[col] = df[col].dt.strftime("%Y-%m-%d %H:%M:%S.%f")
    return df.to_dict(orient="records")


def ceil_timestamp(t, timeframe, trade_time_offset=3):
    """Round timestamp to the next timeframe.

    For example if the timestamp is 2023-01-01 10:20:25.123 and the feature_timeframe =
    10S, then the timestamp is rounded up to 2023-01-01 10:20:33.
    # TODO investigate whether I should be zeroing the microseconds - feels wrong
    Args:
        t (pd.Timestamp):
            tz unaware timestamp
        timeframe (str):
            string corresponding to pandas' timeframes https://pandas.pydata.org/
            pandas-docs/version/1.5/user_guide/timeseries.html#timeseries-offset-aliases

    Returns:
        pd.Timestamp

    """
    # t = t.replace(microsecond=0)-pd.Timedelta(seconds=trade_time_offset)
    t -= pd.Timedelta(seconds=trade_time_offset)
    timeframe = timeframe.replace("m", "T")
    t = t.ceil(timeframe) + pd.Timedelta(seconds=trade_time_offset)
    return t


def update_tick_data(symbols, data, new_data):
    """Update tick data.

    Args:
        symbols (list):
            list of symbols in data
        data (dict[pd.DataFrame]):
            dictionary of dataframes with tick data
        new_data (dict[pd.DataFrame]):
            dictionary if dataframes with tick data

    Returns:
        dict[pd.DataFrame]
            up to date tick data

    """
    for symbol in symbols:
        df = data[symbol]
        df = df[df["time_msc"] < df["time_msc"].iloc[-1].replace(microsecond=0)]
        # df = df[df["time_msc"] < now.replace(microsecond=0).replace(tzinfo=None)]
        df = pd.concat([df, new_data[symbol]], axis=0)
        hours = 24
        if (df["time_msc"].max() - pd.Timedelta(hours=24)).dayofweek > 4:
            hours += 48
        df = df[df["time_msc"] > (df["time_msc"].max() - pd.Timedelta(hours=hours))]
        df.reset_index(inplace=True, drop=True)
        data[symbol] = df
    return data


def download_tick_data(config, symbol, dt0, dt1):
    """Download tick data.

    Downloads tick data between two datetime, dt0 and t1

    #TODO make work for multi-broker

    Args:
        config (pydantic.BaseModel):
            as defined in 'agent_config.py'
        symbol (str):
            trading instrument, e.g. EURUSD
        dt0 (datetime.datetime):
            starting datetime
        dt1 (datetime.datetime):
            ending datetime - non inclusive i think


    """
    port = mt5_api_port_map[config.broker]["general"]
    try:
        _ = requests.get(f"http://127.0.0.1:{port}/healthcheck").json()
    except Exception as e:
        logger.warning(f"Connection Error: http://127.0.0.1:{port} - {str(repr(e))}")
        start_mt5_api(config.broker, "general")
        sleep(15)

    resp = requests.get(f"http://127.0.0.1:{port}/healthcheck").json()
    assert resp["status"] == "ok", f"http://127.0.0.1:{port} failed to initialize"

    resp = requests.post(f"http://127.0.0.1:{port}/init", json=config.mt5.dict())
    d_request = {
        "symbol": symbol,
        "dt0": dt0.strftime("%Y-%m-%d %H:%M:%S.%f"),
        "dt1": (dt1 + relativedelta(days=1)).strftime("%Y-%m-%d %H:%M:%S.%f"),
    }
    resp = requests.get(
        f"http://127.0.0.1:{port}/get_tick_data",
        json=d_request,
        timeout=120,
    ).json()
    df = pd.DataFrame(resp)
    df["time_msc"] = pd.to_datetime(df["time_msc"], unit="ms")

    logger.info(f"{config.broker} {symbol} tick data downloaded")

    return df
