#!/bin/bash
cd /home/tbm/Documents/project_iot
source ./venv/bin/activate
echo $(pwd)
#cd scripts/
python dht11.py
