"""Constants.

Static variables and parameters that are used throughout the app.

#TODO convert to yaml?

"""
from __future__ import annotations

import os
from pathlib import Path

root_dir = str(Path(os.path.dirname(__file__)).parents[2])

mt5_api_port_map = {
    "metaquotes": {
        "general": 2000,
        "EURUSD": 2001,
    },
}


mt5_creds = {
    "metaquotes": {
        "demo": [
            {
                "server": "MetaQuotes-Demo",
                "login": 74538434,
                "password": "Rl!cUf8h",
            },
        ],
    },
}

# Even though pip val may seem trivial for forex,
# It is different for futures contracts
trading_instruments = {
    "metaquotes": {
        "EURUSD": {
            "pip": 1e-4,
            "pip_val": 100,
            "contract_size": 100_000,
            "currency": "USD",
            "commission": 4.0,
        },
        "ND100m": {
            "pip": 1.0,
            "pip_val": 100,
            "contract_size": 10,
            "currency": "USD",
            # unknown for demo account because futures and CFDs can't be traded
            # on demo account
            "commission": 10.0,
        },
        "XAUUSD": {
            "pip": 0.1,
            "pip_val": 100,
            "contract_size": 100,
            "currency": "USD",
            "commission": 4.0,
        },
        "AUDJPY": {
            "pip": 1e-2,
            "pip_val": 10_000,
            "contract_size": 100_000,
            "currency": "JPY",
            "commission": 4.0,
        },
        "USDJPY": {
            "pip": 1e-2,
            "pip_val": 10_000,
            "contract_size": 100_000,
            "currency": "JPY",
            "commission": 4.0,
        },
    },
}
