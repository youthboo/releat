# Getting Started

## Installation

### Prerequisites

- Linux or WSL (for Windows OS)
- Docker
- VSCode (or your preferred IDE)

### Run Container

The simplest method is to use VSCode's Dev Container extension. The configuration is already set up in the `.devcontainer` folder. See the [VSCode's guide] on how to get it running. For alternative ways to build from the Dockerfile or run the container see the [developer notes on containerisation](<development_notes/releat_dockerfile.md#building-the-container>).

[VSCode's guide]: https://code.visualstudio.com/docs/devcontainers/tutorial

Install library, activate local environment, build the python wheel and install the current project:

```
poetry install
source activate ./.venv
poetry build
pip install --user ./dist/releat-0.0.1-py3-none-any.whl --force-reinstall --no-deps
```


### Start Services

Start Aerospike, Ray and MetaTrader5:

```
releat start
```

Note:

- Check that the correct number of gpus are being passed through

Troubleshooting:

- Upon first open, you need to click autotrading + click add account in order for MT5 to connect to servers, otherwise it just hangs

- If the wine gui is frozen or you can't click on buttons or resizing windows causes distortion, restart your linux or wsl machine or container

- You may may need to manually log into MT5 and click on the Autotrade / Algorithm button to enable api access

- If MetaTrader5 does not start up and there's no error message, rebuild container (i.e. start a new container and run an entrypoint script of click on the rebuild container option in VSCode's Dev Container)


### Configure Agent

Placeholder

### Download Data

Placeholder

### Build Training Dataset

Placeholder

### Train Agent

Placeholder

### Deploy Agent

Placeholder
