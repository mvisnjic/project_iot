#!/bin/bash
source instance/bash.cfg
cd $PATH_TO_PROJECT
source ./venv/bin/activate
python thingnet/dht11.py
