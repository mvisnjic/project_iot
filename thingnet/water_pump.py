import time
import RPi.GPIO as GPIO
from datetime import datetime
import logging
import os
import sys
from dotenv import load_dotenv
import rpi_controller as rpi_controller

load_dotenv()

logger = logging.getLogger('water_pump-script')
LOG_DIR = os.getenv('LOG_DIR')

if LOG_DIR is None:
    raise ValueError("LOG_DIR is not set in the environment variables.")

log_file = os.path.join(LOG_DIR, 'water_pump-script.log')
logging.basicConfig(filename=log_file, level=logging.INFO)
    
GPIO.setwarnings(False)

number_of_relay = sys.argv[1]
run_time = sys.argv[2]
number_of_retries = sys.argv[3]

rpi_controller.run_water_pump('water_pump-script', number_of_relay, run_time, number_of_retries)

