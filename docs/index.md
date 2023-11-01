# Welcome to ReLeAT

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

## Key features

- A single container for developing, training, deploying and trading for MetaTrader5 for Linux and Windows (via WSL)
- A simple command line interface to orchestrate the end-to-end process.
- Configuration files that define each step for a specific agent. These are structured to facilitate rapid experimentation and easy integration with Ray's Tune module. types, etc.
- Focuses on Medium Frequency Trading strategies (>1 second and <1 day) using tick data as the input for each step. General latency of the system is ~0.1-3s depending on the complexity of feature engineering and model and resources available.
- In contrast to most other python packages that focus on a deep coverage on one part of the algorithmic trading process, this framework focuses on rapid experimentation lifecycles from idea to deploying and tracking paper trades.

## Documentation Structure

Note this is still a work in progress.

### Getting Started

- [Installation](./getting_started/installation.md) - instructions on how to build or download the docker container
- [Basic Usage](./getting_started/basic_usage.md) - an example on how to build a feature set, train, deploy and trade a RL strategy for EURUSD on a metaquotes demo account
- [Architecture](./development_notes/architecture/overview.md) - a high level overview of the conceptual architecture and repository structure

### Examples

A collection of jupyter notebooks to show how different components work. Note that these notebooks are stored in `docs/examples`

### Development Notes

- [Containerisation](./development_notes/releat_dockerfile.md) - detailed explanation on the design choices for the DockerFile

### Troubleshooting

[Troubleshooting](./troubleshooting/troubleshooting.md) provides guidance on some the common issues that might arise

## Contributing
ReLeAT is an open-source project and we're always looking for contributors and collaborators to make this project even better! Contribution Guidelines are in progress.

## License

ForexRL is distributed under the MIT License. Feel free to use, modify, and share the library according to the terms outlined in the license.
