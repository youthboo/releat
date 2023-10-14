# ReLeAT

REinforcement LEarning for Algorithmic Trading is a python framework for learning medium frequency trading algorithms for MetaTrader 5 (other trading platforms are planned for the future).

DISCALIMER: The information provided herein is for educational and informational purposes only and should not be construed as financial advice. It is not a recommendation to trade or invest real money. Always exercise your own judgment and use common sense when making financial decisions.

## Vision

To build a collaborative community where software engineers, data scientists, RL researchers, quants and finance and economic experts can share knowledge. This framework covers the end-to-end process including:
- extracting data from a MetaTrader5
- building custom features from tick data
- gym environment factory to simulate the trading environment
- training a reinforcement learning and/or machine learning algorithms (Tensorflow)
- deploying trained models
- executing trades

In progress:
- additional platforms including Interactive Brokers and Binance
- custom features for candle data and macroeconomic events
- incoporate other deep learning frameworks such as PyTorch
- better sofware development practices, CI/CD, MLOps, tests
- examples for deployment to cloud to AWS and GCP
- monitoring and observability

## Key features:

- A single container for developing, training, deploying and trading for MetaTrader5 for Linux and Windows (via WSL)

- A simple command line interface to orchestrate the end-to-end process.

- Configuration files that define each step for a specific agent. These are structured to facilitate rapid experimentation and easy integration with Ray's Tune module. types, etc.

- Focuses on Medium Frequency Trading strategies (>1 second and <1 day) using tick data as the input for each step. General latency of the system is ~1-3s depending on the complexity of feature engineering and model and resources available.

- In contrast to most other python packages that focus on a deep coverage on one part of the algorithmic trading process, this framework focuses on rapid experimentation lifecycles from idea to deploying and tracking paper trades. [FinRL](https://github.com/AI4Finance-Foundation/FinRL) and their associated repos are the most similar. The key difference is that this framework focuses on Forex data.

## Prerequisites

- Docker
- Linux or WSL (for windows machine)

## Installation

1) Clone the repositry

```
git clone https://github.com/releat215/releat.git
```

2) Navigate to repository folder

```
cd releat
```

3) Download and run prebuilt docker container

Instructions to build to container from the DockerFile or develop using VSCode's dev containers can be found in the [developer notes](docs/developer_notes/releat_dockerfile.md). Code is containerised to provide consistency (especially when setting up MT5 in linux), easy deployment and scalability.

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

## Usage

This is an example of how to train and deploy a simple agent that trade EURUSD. For more information and/or trouble shooting guides, see the section on [getting started](docs/getting_started.md).

Notes:
- example only works Monday to Friday GMT+2/3 due to metaquotes not allowing data extract or trades on weekend demo accounts.
- In this example, the feature space, RL model and trading configurations are specified in the `agents/t00001` folder.
- Steps 4+ are be blocking processes, so open a new terminal to run in parallel.

1) Connect to running docker container

If opening a new terminal, connect interactively to the running docker container:

```
docker exec -it releat /bin/bash
```

2) Start services

Starts services necessary to train, deploy and monitor the reinforcement
learning trading agent:
- Aerospike: In-memory database to store features and hyperparameters
- Ray: Manages compute and provides RL training and inference logic
- MT5: Download data and trade for forex and futures (depending on broker)
- Tensorboard: Monitor RL training progress
- Redis: In memory cache for storing RL predictions

IMPORTANT: If it is the first time starting up the docker container, or if it has been rebuilt, log in the your MT5 account manually and click the allow autotrading button. If not, steps 3+ will not work.

```
releat start
releat launch-mt5-api metaquotes general
```


3) Build training data

Build the features defined by the `feature_config.py` script and upload to Aerospike.

```
releat build-train-data t00001
```

4) Train model

RL model is defined in `agent_model.py` and the training hyperparameters are defined in `agent_config.py`, including the number of iterations to run the training. Checkpoints are saved locally, which can then used for deployment

```
releat train t00001
```

5) Generate signal

Using the artifacts generated by the training process, this generate signal process is deployed to continuously:
- extract data from MT5
- build features
- makes predictions by invoking the RL agent
- pushes predictions to redis
- loads the latest checkpoint

The frequency of the prediction is controlled by the configs set in `agent_config.py`

```
releat generate-signal t00001
```

6) Launch trader

The trader is agent version agnostic (for now) and is deployed to:
- gets the predictions from redis (in the future it will have capability to aggregate predictions from multiple different RL agents)
- applies some risk logic (such as lot size scaling)
- applies other operational logic (i.e. minimum position hold time, forced close at session close, etc.)
- executes open or close actions for long or short positions

```
releat launch-trader
```


## Contributing

Actively looking for contributors and collaborators to make this project even better! Code quality is average and improvements are in progress. Please:

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
