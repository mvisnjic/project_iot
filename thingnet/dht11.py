import time
import Adafruit_DHT
import RPi.GPIO as GPIO
from datetime import datetime
from RPLCD.gpio import CharLCD
import logging
import os
from dotenv import load_dotenv
import rpi_controller as rpi_controller

load_dotenv()

logger = logging.getLogger('dht11-script')
LOG_DIR = os.getenv('LOG_DIR')

if LOG_DIR is None:
    raise ValueError("LOG_DIR is not set in the environment variables.")

log_file = os.path.join(LOG_DIR, 'dht11-script.log')
logging.basicConfig(filename=log_file, level=logging.INFO)

sensor = Adafruit_DHT.DHT11

DHT_PIN = int(os.getenv('DHT_GPIO_PIN'))
NUMBER_OF_MEASUREMENTS = int(os.getenv('NUMBER_OF_MEASUREMENTS'))

final_temperature = 0

print("Starting - Datetime:", datetime.now(), "\n")

for i in range(NUMBER_OF_MEASUREMENTS):
    try:
        print("Očitanje", i+1)
        measurement = rpi_controller.read_dht_sensor(sensor, DHT_PIN)
        final_temperature = measurement['temperature']
        final_humidity = measurement['humidity']
        format_LCD = '{0:0.1f}*C {1:0.1f}%'.format(measurement['temperature'],measurement['humidity'])
        if(i+1 < NUMBER_OF_MEASUREMENTS):
            time.sleep(1)
    except RuntimeError as error:
        logger.error(error)
        time.sleep(1)
        continue
    except Exception as error:
        logger.error(error)
        raise error

RELAY_PIN = int(os.getenv('RELAY_PIN_1'))
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logger.info(f'Final temperature,humidity:{format_LCD} Datetime: {current_time}')

if(int(final_temperature) <= 15 and int(final_temperature) > 0):
    try:
        past_input_value = rpi_controller.prepare_relay_and_get_input(RELAY_PIN)
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        logger.info(f'Toggled heater(relay_1-pin_{RELAY_PIN}) ON.')
        rpi_controller.setLCDMessage(final_temperature, final_humidity)
    except:
        logger.error(f'Failed to toggle relay ON!')
else:
    try:
        past_input_value = rpi_controller.prepare_relay_and_get_input(RELAY_PIN)
        GPIO.output(RELAY_PIN, GPIO.LOW)
        logger.info(f'Toggled heater(relay_pin {RELAY_PIN}) OFF.')
        rpi_controller.setLCDMessage(final_temperature, final_humidity)
    except:
        logger.error(f'Failed to toggle relay OFF!')

input_value = GPIO.input(RELAY_PIN)
logger.info(f'Relay current state: {input_value}, past state: {past_input_value}')
print("\nFinished - datetime:", datetime.now(), "\n")
