"""Generate signals.

Generates signals according to an agent version and pushes the json prediction
to redis json. Key to fetch prediction is the agent version. Each new record
currently overwrites the value in redis

TODO test stream or other functionality for redis

TODO wrap in a whole function + add to cli + manage services

"""
from __future__ import annotations

from time import sleep

from releat.trader.signal_generator import SignalGenerator
from releat.utils.configs.config_builder import load_config
from releat.utils.time import get_current_mt5_time
from releat.utils.time import mt5_hour_diff
from releat.utils.time import wait_till_action_time


agent_version = "t00001"
config = load_config(agent_version)

# initialis signal generator
sg = SignalGenerator(agent_version)

hour_diff = mt5_hour_diff()
now = get_current_mt5_time(hour_diff).strftime("%Y-%m-%d %H:%M:%S.%f")
sg.pm.now = now
sg.initialise_data(now)


while True:
    # sleep so that the data and action is collected at the right interval
    # i.e. if the trade_timeframe = 10s and trade_time_offset = 3s, then
    # sleeps until 13th, 23rd, 33rd, 43rd and 53rd second of each minute
    now = get_current_mt5_time(hour_diff)
    # TODO should wait_till_action_time take now as a string or datetime?
    weekend, sleep_time = wait_till_action_time(
        config.raw_data.trade_timeframe,
        config.raw_data.trade_time_offset,
        now,
    )
    sleep(sleep_time)
    if weekend:
        continue

    # update the now variable with current time
    now = get_current_mt5_time(hour_diff).strftime("%Y-%m-%d %H:%M:%S.%f")
    sg.pm.now = now

    # extract tick data and update features
    sg.update_data(now)

    # predict data - this gets pushed to redis
    pred = sg.predict()
