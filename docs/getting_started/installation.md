# Installation

## Prerequisites

- Docker
- Linux or WSL (for windows machine, preferably Ubuntu 20.04)

## Installation

### 1) Clone the repositry

```
git clone https://github.com/releat215/releat.git
```

### 2) Navigate to repository folder

Assuming that the repository is cloned to the default destination, navigate to the repository.

```
cd releat
```

### 3) Build or download docker container

Developing in the docker container is recommended because:
- Trained RL agents can be easily deployed to multiple instances
- Collaborators are working with the same stack and package versions
- Provides utility for installing MetaTrader5 in wine

The docker container can be build by:

```
docker build -t releat -f ./infrastructure/releat/Dockerfile .
```

Alternatively, the container has been pre-built and can be fetched from docker:

```
docker pull releat215/releat:1.0
```

Note:
- Detailed notes on the components of the DockerFile are in the [developer notes](developer_notes/releat_dockerfile.md)

### 4) Run docker container

Run and connect to the docker container. Depending on your IDE, there are two main methods:
- VSCode's Dev Container
- connecting to a running docker container

#### VSCode's Dev Container

The scripts for setting up VSCode's dev container is stored in `.devcontainer`. The following shows how to start up and connect to the dev container:

GET PICTURE OF CONNECT TO DEV CONTAINER

Note:
- For more infromation on how to launch the dev container, see [VSCode's documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- Docker must be started
- If you do not have gpus, deleted the line `'--gpus==all'` in the `runArgs` key of the `.devcontainer/devcontainer.json` file

#### Connect to a running docker container

Firstly run the docker container:

```
docker run \
    --net host \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd):/workspaces/releat \
    -e DISPLAY \
    --gpus all \
    -it \
    --name releat \
    releat215/releat:1.0
```

Then you can connect to the running container:

```
docker exec -it releat /bin/bash
```

Note:
- Detailed notes on the purpose of each argument can be found in the [developer notes](developer_notes/releat_dockerfile.md#docker-run)
- When running python scripts, make sure to navigate to correct folder and activate the environment: `cd /workspaces/releat && source activate ./.venv`

### 5) Update CLI

The CLI uses cached function. If you update the source code, the `releat` package needs to be rebuilt and re-installed to reflect updated / new functions:

```
source activate ./.venv
poetry build
pip install --user ./dist/releat-0.0.1-py3-none-any.whl --force-reinstall --no-deps
pip uninstall releat -y
poetry install
```

Note:
- The final uninstall and install removes the installed wheel (with cached functions) and re-installs the package in editable mode so that futher edits can be made to the source code.
