# ReLeAT

REinforcement LEarning for Algorithmic Trading is a python framework for learning medium frequency trading algorithms for forex. Other trading instruments such as crypto and futures will be implemented in development. The aim is to democratise trading by providing a platforms where developers, data scientists and researchers with different specialisations can collaborate.

## Key features:

- A single container for developing, training and trading for MetaTrader5 for Linux and Windows (via WSL)

- Each trading algorithm is defined by a set of configuration files. These configs define:

    - how features are built from tick data,
    - machine learning model / neural network architecture
    - reinforecement learning algorithm hyperparameters
    - gym environment (how the reward is specified, the agent's permissible trading types, etc.)
    - trading execution and risk management

- Focuses on Medium Frequency Trading strategies (>1 second and <1 day) using tick data as the input for each step. General latency of the system is ~1-3s depending on the complexity of feature engineering and model and resources available.

- Configuration is formatted for easy hyperparameter tuning

- In contrast to most python packages that provide a broad coverage of a part of the reinforcement learning algorithmic trading process, this package has narrow stack that focuses on the end-to-end process from alpha ideation to deploying your algorithm.

## Prerequisites

- Docker
- Linux or WSL (for windows machine)

## Installation

Container environments are preferred to ensure that the development and deployment environments are the same.


#### VSCode Dev Containers
If you use VSCode as your IDE, you can use the Dev Container extension, using the provided specification in the `.devcontainer` folder. See the [official guide] on how to start it up.

[official guide]: https://code.visualstudio.com/docs/devcontainers/tutorial


#### Pre-built Docker Image
You can either pull the prebuild image from Docker:

```
docker run \
    --net host \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd):/releat \
    -e DISPLAY \
    -it \
    --name releat \
    releat215/releat:1.0
```

### Build docker image

Using the repo folder as your context, you can build the image using this command. There are some quirks when it comes to running MetaTrader5 on wine, please see [developer notes](developer_notes/releat_dockerfile.md) for more details.

```
docker build -t releat -f ./infrastructure/releat/Dockerfile .
```

## Usage

Placeholder


## Contributing

We welcome contributions from the community to make this project even better! Please:

1) Create an issue

2) Create a new branch to work on your feature or bug fix. Give it a descriptive name.

3) Include tests for your feature or bug fix

4) Create a pull request

Alternatively, if you want to take the project in a different direction, feel free to fork the project.

## Licence

[MIT](https://choosealicense.com/licenses/mit/)

## Maintainer

If you have any questions, please contact:

- releat215@gmail.com
