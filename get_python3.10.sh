#!/bin/bash

PYTHON_VERSION="3.10.2"
# ------------ Get Python version 3.XX  -----------------

sudo apt-get update -y

sudo apt-get install build-essential libncurses5-dev libncursesw5-dev libreadline6-dev libdb5.3-dev libgdbm-dev libc6-dev libbz2-dev libexpat1-dev liblzma-dev zlib1g-dev libsqlite3-dev tk-dev libssl-dev openssl libffi-dev -y

mkdir Python-Installation
cd Python-Installation

wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
tar xzvf Python-${PYTHON_VERSION}.tgz
rm -f Python-${PYTHON_VERSION}.tgz

cd Python-${PYTHON_VERSION}
# These next commands will take some time. Go get a coffee.
sudo ./configure --enable-optimizations
sudo make -j 4
sudo make install

cd ../..
sudo rm -rf Python-Installation

sudo apt-get autoremove -y
sudo apt-get clean

python3.10 -m pip install --upgrade pip


# Link the 'python3' command to the new version of python
# sudo rm /usr/bin/python3
# sudo ln -s /usr/local/bin/python3.10 /usr/bin/python3

# sudo update-alternatives --install /usr/bin/python python /usr/local/bin/python3.10 3

# --------------------------------------------------------
