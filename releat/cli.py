"""CLI for ReLeAT."""
from __future__ import annotations

import typer

from releat.data.pipeline import populate_train_data
from releat.utils import service_manager as sm
from releat.utils.configs.config_builder import load_config
from releat.utils.logging import get_logger
from releat.utils.service_manager import start_services
from releat.utils.service_manager import stop_services

app = typer.Typer()


logger = get_logger(__name__)


@app.command()
def start():
    """Start all services."""
    start_services()


@app.command()
def stop():
    """Stop all services."""
    stop_services()


@app.command()
def start_mt5_api(broker, symbol):
    """Start mt5 api for one broker."""
    sm.start_mt5_api(broker, symbol)


@app.command()
def initialize_training_data(agent_version):
    """Initialise training data."""
    config = load_config(agent_version)
    _ = populate_train_data(config, mode="initialise")


if __name__ == "__main__":
    app()
