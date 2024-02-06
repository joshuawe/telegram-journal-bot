#!/bin/bash
# In terminal run to make executable: chmod +x setupVM.sh

# This is the script for setting up the VM for telegram bot

# Install necessary packages
sudo apt-get update
sudo apt-get install tmux
sudo apt-get install git
sudo apt-get install ranger
sudo apt-get install python3-venv

# Clone the repository
git clone 'https://github.com/joshuawe/telegram-journal-bot'
cd telegram-journal-bot

# create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install local package with pip
pip install -e .

# Create empty database to store user data
python3 src/database_setup.py

echo "> Script is done. <"