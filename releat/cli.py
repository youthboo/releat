"""CLI for ReLeAT."""
from __future__ import annotations

import typer

from releat.data.pipeline import populate_train_data
from releat.utils.configs.config_builder import load_config
from releat.utils.logging import get_logger
from releat.workflows import generate_signals
from releat.workflows import service_manager as sm
from releat.workflows.service_manager import start_services
from releat.workflows.service_manager import stop_services
from releat.workflows.train_rl_agent import train_rl_agent

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
def launch_mt5_api(broker, symbol):
    """Start mt5 api for one broker."""
    sm.start_mt5_api(broker, symbol)


@app.command()
def build_train_data(agent_version):
    """Builds training data."""
    config = load_config(agent_version)
    _ = populate_train_data(config, mode="initialise")


@app.command()
def launch_train_data_updater(agent_version):
    """Periodically updates train data db."""
    logger.info(f"WIP for {agent_version}")


@app.command()
def train(agent_version):
    """Train RL agent."""
    config, AgentModel = load_config(
        agent_version,
        enrich_feat_spec=True,
        load_model=True,
    )
    train_rl_agent(config, AgentModel)


@app.command()
def generate_signal(agent_version):
    """Generate a trading signal."""
    _ = generate_signals.generate_signal(agent_version)


@app.command()
def launch_trader():
    """Launch trading agent."""
    exec(open("./releat/trader/trader.py").read())


if __name__ == "__main__":
    app()
