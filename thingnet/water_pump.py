import time
import RPi.GPIO as GPIO
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
import rpi_controller as rpi_controller

load_dotenv()

logger = logging.getLogger('water_pump-script')
LOG_DIR = os.getenv('LOG_DIR')

if LOG_DIR is None:
    raise ValueError("LOG_DIR is not set in the environment variables.")

log_file = os.path.join(LOG_DIR, 'water_pump-script.log')
logging.basicConfig(filename=log_file, level=logging.INFO)

def run_water_pump(relay_pin, run_time ,number_of_retries):
    try:
        past_input_val = rpi_controller.prepare_relay_and_get_input(relay_pin)
        turn_on = rpi_controller.toggleRelay('water_pump-script', relay_pin, 'on')
        
        if(turn_on):
            logger.info(f'Relay current state:{turn_on}, before state:{past_input_val}')
            time.sleep(run_time)
            past_input_val = rpi_controller.prepare_relay_and_get_input(relay_pin)
            turn_off = rpi_controller.toggleRelay('water_pump-script', relay_pin, 'off')
            
            if(turn_off):
                logger.info(f'Relay current state:{turn_off}, before state:{past_input_val}')
                return True
            for i in range(number_of_retries):
                logger.info(f'Failed to turn off water pump. Trying again... attempt {i+1}/{number_of_retries}')
                turn_off = rpi_controller.toggleRelay('water_pump-script', relay_pin, 'off')
        logger.error("Failed to turn on water_pump.")
    except:
        logger.error("Water pump exception! Calling function again...")
        return run_water_pump(RELAY_PIN, run_time, number_of_retries)
    
logger.info("Starting - Datetime:", datetime.now(), "\n")

RELAY_PIN = int(os.getenv('RELAY_PIN_4'))
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

past_input_value = GPIO.input(RELAY_PIN)

run_water_pump(RELAY_PIN, 20, 5)

new_val = GPIO.input(RELAY_PIN)
logger.info(f'Relay current state: {new_val}, past state: {past_input_value}')
logger.info("\nFinished - Datetime:", datetime.now(), "\n")
