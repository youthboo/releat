"""CLI for ReLeAT."""
from __future__ import annotations

import typer

from releat.utils import service_manager as sm
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
    """Stop all services."""
    sm.start_mt5_api(broker, symbol)


if __name__ == "__main__":
    app()
