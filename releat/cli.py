"""CLI for ReLeAT."""
from __future__ import annotations

import typer

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


if __name__ == "__main__":
    app()
