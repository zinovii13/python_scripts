#!/bin/bash

echo START

# switch to venv dir
cd pipenv

#create venv
sudo apt install python3.9-venv
python3.9 -m venv venv

# activate venv
source venv/bin/activate

# install pipenv
pip install pipenv

# load pipenv requirements
pipenv install

echo DONE
read -rsp $'Press any key to continue...\n' -n 1 key