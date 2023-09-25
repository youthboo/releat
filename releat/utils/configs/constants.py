"""Constants.

Static variables and parameters that are used throughout the app.

#TODO convert to yaml?

"""
from __future__ import annotations

mt5_api_port_map = {
    "metaquotes": {
        "trader": 2000,
        "EURUSD": 2001,
    },
}

mt5_demo_configs = [
    {
        "broker": "metaquotes",
        "server": "MetaQuotes-Demo",
        "login": 5017261249,
        "password": "!7XtGwMs",
    },
]
