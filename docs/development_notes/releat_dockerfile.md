# Building the ReLeAT DockerFile

Summary of design considerations for the Dockerfile that has the following features:

- Install and run MetaTrader5 and python in wine
- Rllib in linux container with Nividia GPU enabled
- Poetry to manage package dependency
- Aerospike as databse tool


## Key Points

- Check aerospike versions because they tend to be updated quite frequently

- User the repo folder as the context when building and running

- On first start up of MetaTrader5, you need to manually click on the 'Accounts' button to allow it to connect to broker servers. After logging in you need to manually click the 'Allow Autotrading' button - slightly weird behaviour from running MetaTrader5 on wine.

- Future work - updating packages to latest version

## Design Considerations

### Base layer

- Ubuntu 20.04 was used as the base image - could upgrade in the future.

- `DEBIAN_FRONTEND=noninteractive` to accept all default options when installing and
removing software (i.e. apt-get install). This prevents questions from blocking
the installation process

- Set environment paths so that Miniconda, MetaTrader5 and python environments
are saved in the correct place and/or easily searchable.

- `MT5_PATH` is saved as an environment variable because the entrypoint script
check whether this file exists. If not, then it will install MT5

- Set environment display to 0 to pass through screen. Not sure if this is necessary.
But some wine windows apps (i.e. Python and MetaTrader5) cannot be installed headlessly

- Tensorflow version is set to 2.11.0 - could be upgraded in the future

- Python version is set to 2.10.10 - couldn't upgrade this to 2.11 because at the time,
the aerospike python package and rllib was incompatible / not stable

``` { .sh .no-copy }
FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

ENV PATH="${PATH}:/root/miniconda3/bin:/root/.local/bin"
# Location of linux python env
ENV PY_PATH="./.venv"
# Metatrader path
ENV MT5_PATH="/root/.wine/drive_c/Program Files/MetaTrader 5/terminal64.exe"

ENV DISPLAY :0

# Tensorflow version
ENV TF_V="2.11.0"
# Python version
ENV PY_V="3.10.10"
```

### Wine

Wine enables the running of Windows software on Linux systems.
For other options, see this guideline for [installing and running wine].

- `WINEDLLOVERRIDES="mscoree,mshtml="` [disables the Mono installer dialog] allowing it to
be installed in the Dockerfile headlessly instead of in the entrypoint script.

- `WINEDEBUG="fixme-all,err-all"` suppresses most of the warnings, reducing log volume

- `WINEPREFIX="/root/.wine"` helps processes find the installation location of wine

- `dpkg --add-architecture i386` enables the installation of multiarch binaries

- install development version of wine - could also use stable

- `winecfg -v win10` sets the windows 10, necessary for python and MT5

- `wineserver -w` waits until currently running wineserver terminates. Not sure if
this is necessary

[disables the Mono installer dialog]: https://forum.winehq.org/viewtopic.php?t=16320
[installing and running wine]: https://wiki.archlinux.org/title/Wine_package_guidelines

``` { .sh .no-copy }
# Wine configs
ENV WINEDLLOVERRIDES="mscoree,mshtml="
ENV WINEDEBUG="fixme-all,err-all"
ENV WINEPREFIX="/root/.wine"


# Install wine
RUN apt-get update \
	&& apt-get install -y wget gnupg2 dialog apt-utils software-properties-common curl make git tzdata \
	&& dpkg --add-architecture i386 \
	&& mkdir -pm755 /etc/apt/keyrings \
	&& wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key \
	&& wget -nc https://dl.winehq.org/wine-builds/ubuntu/dists/focal/winehq-focal.sources \
	&& mv winehq-focal.sources /etc/apt/sources.list.d/ \
	&& apt-get update \
	&& apt-get install -y --install-recommends winehq-devel \
	&& apt-get remove -y winbind \
	&& apt-get install -y winbind \
	&& rm -rf /var/lib/apt/lists/* /winehq.key \
	&& winecfg -v win10 \
	&& wineserver -w
```

Install mono and gecko, wine packages that a necessary to make windows applications
work. Depending on what version of wine is installed, install the appropriate
[mono version] and [gecko version]. Reboot and remove installation files once
installed

[mono version]: https://wiki.winehq.org/Mono
[gecko version]: https://wiki.winehq.org/Gecko
``` { .sh .no-copy }
# Install wine mono and gecko
RUN wget https://dl.winehq.org/wine/wine-mono/8.0.0/wine-mono-8.0.0-x86.msi \
    && wget https://dl.winehq.org/wine/wine-gecko/2.47.4/wine-gecko-2.47.4-x86.msi \
    && wget https://dl.winehq.org/wine/wine-gecko/2.47.4/wine-gecko-2.47.4-x86_64.msi \
	&& wineboot \
	&& wine wine-mono-8.0.0-x86.msi /quiet \
    && wine wine-gecko-2.47.4-x86.msi /quiet \
    && wine wine-gecko-2.47.4-x86_64.msi /quiet \
	&& rm wine-mono-8.0.0-x86.msi wine-gecko-2.47.4-x86.msi wine-gecko-2.47.4-x86_64.msi
```

### Conda and Poetry

Miniconda and poetry for manage python packages. [Both are required]
because of GPU. Miniconda is used to install nvidia packages whilst poetry is for pure
python. `eval "$(conda shell.bash hook)"` sets up shell functions for Conda.

[Both are required]: https://stackoverflow.com/questions/70851048/does-it-make-sense-to-use-conda-poetry
``` { .sh .no-copy }
# Install Miniconda and Poetry
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh \
	&& eval "$(conda shell.bash hook)" \
	&& curl -sSL https://install.python-poetry.org | python3 -
```

### Aerospike

[Aerospike] is a real-time in memory database, which will be used to for storing
observations for the reinforment learning training process. This is installed last
because version are updated frequently, so we only need to rebuild the last layer.

Note: check aerospike versions regularly

[Aerospike]: https://aerospike.com/
``` { .sh .no-copy }
# aerospike server version
ARG AS_V="6.4.0.1"
# aerospike tool version
ARG AT_V="9.0.0"
# Installing aerospike
RUN wget -O aerospike.tgz https://download.aerospike.com/artifacts/aerospike-server-community/${AS_V}/aerospike-server-community_${AS_V}_tools-${AT_V}_ubuntu20.04_x86_64.tgz \
    && tar -xvf aerospike.tgz \
    && cd aerospike-server-community_${AS_V}_tools-${AT_V}_ubuntu20.04_x86_64 \
	&& ./asinstall \
	&& cd .. \
	&& rm aerospike.tgz

ENTRYPOINT ["/bin/bash"]
```

## Entrypoint

The default entrypoint is the bash terminal. An entrypoint script is included in that folder and run depending on how you plan on accessing the container. The next section explains each component of the entrypoint script, followed by the different ways to [build](#building-the-container) and [run](#running-the-container) the container


### Entrypoint logic

- `#!/bin/bash` - when using VSCode's devcontainer functionality must use bash because
sh doesn't work, not sure why

### Linux python environment

- check if `./.venv` folder already exists, if so we can skip the installation of
python libraries

- Create python environment. Note this is done in entrypoint rather than Dockerfile
so that the installed files are in the same location as the repo within the binded mount.
Works well for developing in VSCode's devcontainer, need to test more when using other
IDEs.

- Currently we're still using an old version of tensorflow - see notes below for future
version for python

- For GPU usage, we need conda to install cuda packages. Then everything else can be
installed by pip

- Make sure to lock tensorflow version in poetry lock file, then install all other
packages using poetry

``` { .sh .no-copy }
if test -d "./.venv"; then
    echo "Conda environments installed"
else
    echo "install linux packages"
    conda create --prefix ${PY_PATH} python=${PY_V} -y
    eval "$(conda shell.bash hook)"
    conda activate ${PY_PATH}

    # Install linux tensorflow=2.11.0
	conda install -c conda-forge cudatoolkit=11.2.2 cudnn=8.1.0 -y
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
	mkdir -p $CONDA_PREFIX/etc/conda/activate.d
	echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh \
	LD_LIBRARY_PATH=/content/conda-env/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64
	pip install --upgrade pip
	pip install tensorflow==${TF_V}

    # Install linux python packages
    conda install -c anaconda -y
    poetry init --python=~${PY_V}
    poetry add --lock tensorflow=${TF_V}
    poetry install --with rl
    pre-commit install

fi
```

### Wine packages

- Install same version of python in wine. We need this to programmatically extract
data and trade in MT5

- Install python packages via poetry, note this means that when we deploy tensorflow
models, we will be using cpu version only. Currently designed to be a monolith to
simplify networking between applications / container. Might look at a
microservice design in the future

- Needs to be a fresh install each time for the dev container because the gui works
right after install, however doesn't work when you close and re-open vscode.
possibly a wine / linux / wsl issue

- Keep install files for now because deleting them seems to cause an error - I suspect
some kind of race condition where the file is deleted before install is complete.

- Other references: https://github.com/python-poetry/poetry/issues/5037

- Install MT5

``` { .sh .no-copy }

# Installing wine python
echo "installing wine python" \
&& wget https://www.python.org/ftp/python/${PY_V}/python-${PY_V}-amd64.exe \
&& wine python-${PY_V}-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0 \
# && rm python-${PY_V}-amd64.exe \
&& echo "Python installed successfully"

# Installing wine python packages
echo "installing python packages" \
&& wine pip install poetry \
&& wine poetry config virtualenvs.create false \
&& wine poetry config virtualenvs.in-project false \
&& wine poetry install --only mt5

# Installing MT5
echo "Installing MT5" \
&& wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe \
&& wine mt5setup.exe /auto \
# && rm mt5setup.exe \
&& echo "MT5 installed successfully"

fi
```


### Side notes

- [Future versions of tensorflow] should be installed like this:

[Future versions of tensorflow]: https://www.tensorflow.org/install/pip

```
    conda install -c conda-forge cudatoolkit=11.8.0
    python3 -m pip install nvidia-cudnn-cu11==8.6.0.163 tensorflow==2.13.0
    mkdir -p $CONDA_PREFIX/etc/conda/activate.d
    echo 'CUDNN_PATH=$(dirname $(python -c "import nvidia.cudnn;print(nvidia.cudnn.__file__)"))' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
    echo 'export LD_LIBRARY_PATH=$CUDNN_PATH/lib:$CONDA_PREFIX/lib/:$LD_LIBRARY_PATH' >> $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
    source $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh
```

- start aerospike - may leave this for later because we may want to put aerospike
configs into the folder of each agent / experiment

```
start aerospike
asd --config-file ./infrastructure/aerospike.conf
```

## Building the Container

Using the repo folder as your context / current working directory, the DockerFile can be built by the following command.

```
docker build -t releat -f ./infrastructure/releat/Dockerfile .
```

## Running the Container

This container can be used for development in 2 main ways:

- VSCode's devcontainer functionality

- docker container with a mount

### VSCode devcontainer

If you use VSCode as your IDE, you can use the Dev Container extension, using the provided specification in the `.devcontainer` folder. See the [official guide] on how to start it up.

- Note that in the `.devcontainer/devcontainer.json`, we invoke the entrypoint script after the docker image has been started up to install the project and MetaTrader5

- Upon first open, you need to click autotrading + click add account in order for MT5 to connect to servers, otherwise it just hangs

- If the wine gui is frozen or you can't click on buttons or resizing windows causes distortion, restart your linux or wsl machine or container


Side Notes:

- Future low priority work to make it more stable: If Developing on Windows system via WSL, to pass through Metatrader GUI, follow [this guide] and [this discussion]

[official guide]: https://code.visualstudio.com/docs/devcontainers/tutorial

### docker run

Assumes your context / current working directory is the repo folder. We can build the docker image by:

``` { .sh .no-copy }
docker run \
    --net host \
    -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $(pwd):/releat \
    -e DISPLAY \
    -it \
    --name test \
    --gpus=all \
    releat215/releat:1.0 \
    -c './releat/infrastructure/releat/entrypoint.sh && cd releat && /bin/bash'
```

- `--net host` container shares network with the host, meaning we don't need to manually listen to ports - i think this also allows the container to access the internet

- `-v /tmp/.X11-unix:/tmp/.X11-unix` passes through the display. Necessary because MT5 can't be run headlessly (without lots of tinkering)

- `-v $(pwd):/releat` mounts

- `-e DISPLAY` Maybe its necessary to pass through the display

- `-v $(pwd):/releat` mounts the repo to the corresponding location in the container

- `--gpus=all` passes through GPUs from your machine to the container



- Still need add in code that binds the location of the repo / fix this docker run code

[this guide]: https://kenny.yeoyou.net/it/2020/09/10/windows-development-environment.html
[this discussion]: https://stackoverflow.com/questions/61110603/how-to-set-up-working-x11-forwarding-on-wsl2/63092879#63092879
