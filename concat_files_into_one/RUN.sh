#!/bin/bash

echo START

pipenv/venv/bin/python script/script.py

echo DONE
read -rsp $'Press any key to continue...\n' -n 1 key