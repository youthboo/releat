#!/bin/bash

if test -d "./.venv"; then
    echo "Conda environments installed"
else
    echo "install linux packages"
    conda create --prefix ${PY_PATH} python=${PY_V} -y
    eval "$(conda shell.bash hook)"
    conda activate ${PY_PATH}

    # Install linux tensorflow=2.11.0
    echo "installing tensorflow"
	conda install -c conda-forge cudatoolkit=11.2.2 cudnn=8.1.0 -y
	export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/
	mkdir -p $CONDA_PREFIX/etc/conda/activate.d
	echo 'export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$CONDA_PREFIX/lib/' > $CONDA_PREFIX/etc/conda/activate.d/env_vars.sh \
	LD_LIBRARY_PATH=/content/conda-env/lib:/usr/local/nvidia/lib:/usr/local/nvidia/lib64
	pip install --upgrade pip
	pip install tensorflow==${TF_V}
    echo "tensorflow installed"

    # Install linux python packages
    echo "installing other packages"
    conda install -c anaconda -y
    poetry init --python=~${PY_V}
    poetry add --lock tensorflow=${TF_V}
    poetry install --with rl
    pre-commit install

fi

# See documentation for why it needs to be a fresh install each time
# Installing wine python
echo "installing wine python"
if ! test -f "python-${PY_V}-amd64.exe"; then
wget https://www.python.org/ftp/python/${PY_V}/python-${PY_V}-amd64.exe
fi
wine python-${PY_V}-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
# && rm python-${PY_V}-amd64.exe \
echo "Python installed successfully"

# Installing wine python packages
echo "installing python packages" \
&& wine pip install poetry \
&& wine poetry config virtualenvs.create false \
&& wine poetry config virtualenvs.in-project false \
&& wine poetry install --only mt5

# Installing MT5
echo "Installing MT5"
if ! test -f "mt5setup.exe"; then
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe
fi
wine mt5setup.exe /auto
# && rm mt5setup.exe \
echo "MT5 installed successfully"
