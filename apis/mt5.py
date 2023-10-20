"""MT5 api.

API so that data can be easily shared between linux and wine processes.

#TODO move to redis

"""
from __future__ import annotations

import argparse

from flask import Flask
from flask import request

from releat.connectors.mt5 import MT5Connector
from releat.utils.configs.constants import mt5_api_port_map

argParser = argparse.ArgumentParser(
    description="Start mt5 api",
)

argParser.add_argument("-b", "--broker", help="broker")
argParser.add_argument("-s", "--symbol", help="trading instrument")
args = argParser.parse_args()

app = Flask(__name__)

mt5c = None


@app.route("/init", methods=["POST"])
def initialise_connector():
    """Initialize mt5 connector."""
    global mt5c
    mt5_config = request.json
    mt5c = MT5Connector(mt5_config)
    status = mt5c.initialize()
    if status:
        return {"status": "ok"}, 200
    else:
        return {"status": "fail"}, 200


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    """Checks health of mt5."""
    global mt5c
    status, tinfo = mt5c.check_mt5()
    if status:
        return tinfo._asdict()
    else:
        return str(tinfo)


@app.route("/open", methods=["POST"])
def open_position():
    """Open position."""
    global mt5c
    data = request.json
    return mt5c.open_position_with_retry(**data)


@app.route("/close", methods=["POST"])
def close_position():
    """Close position."""
    global mt5c
    data = request.json
    return mt5c.close_position_with_retry(**data)


@app.route("/get_positions", methods=["GET"])
def get_positions():
    """Get open positions."""
    global mt5c
    df = mt5c.get_positions()
    if df is not None:
        return df.to_dict(orient="records")
    else:
        return {}


@app.route("/get_tick_data", methods=["GET"])
def get_tick_data():
    """Get tick data."""
    global mt5c
    data = request.json
    df = mt5c.get_tick_data(**data)
    if df is not None:
        return df.to_dict(orient="records")
    else:
        return {}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=mt5_api_port_map[args.broker][args.symbol], debug=False)
