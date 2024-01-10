#!/bin/bash

# This script will update the repo with the latest version of the code.
# And also (re)install all required new packages.

git fetch --all
git pull

# activate the virtual environment
source venv/bin/activate
pip install -r requirements.txt