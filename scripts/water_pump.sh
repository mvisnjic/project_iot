#!/bin/bash
source instance/bash.cfg
cd $PATH_TO_PROJECT
source ./venv/bin/activate
python thingnet/water_pump.py $NUMBER_OF_RELAY $RUN_TIME $NUMBER_OF_RETRIES
