import time
import Adafruit_DHT
import RPi.GPIO as GPIO
from datetime import datetime
from RPLCD.gpio import CharLCD
import logging
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
LOG_DIR = os.getenv('LOG_DIR')

if LOG_DIR is None:
    raise ValueError("LOG_DIR is not set in the environment variables.")

log_file = os.path.join(LOG_DIR, 'dht11-script.log')
logging.basicConfig(filename=log_file, level=logging.INFO)
sensor = Adafruit_DHT.DHT11

DHT_PIN = int(os.getenv('DHT_GPIO_PIN'))
number_of_measurements = 5

def setLCDMessage(data):
    lcd = CharLCD(
    pin_rs=15,
    pin_rw=12,
    pin_e=16,
    pins_data=[31, 33, 35, 37],
    cols=16, rows=4,
    numbering_mode=GPIO.BOARD
    )
    
    try:
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        lcd.clear()
        lcd.write_string(f"{data}\r\n{current_time}")
    except Exception as e:
        logger.error(f"Set LCD message failed, error:{e}")

final_temperature = 0

print("Starting - Datetime:", datetime.now(), "\n")

for i in range(number_of_measurements):
    try:
        print("Očitanje", i+1)
        humidity, temperature = Adafruit_DHT.read_retry(sensor, DHT_PIN)
        format_LCD = '{0:0.1f}*C {1:0.1f}%'.format(temperature,humidity)
        print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity), "Datetime -", datetime.now())
        final_temperature = temperature
        final_humidity = humidity
        if(i+1 < number_of_measurements):
            time.sleep(1)
    except RuntimeError as error:
        logger.error(error)
        time.sleep(1)
        continue
    except Exception as error:
        dhtDevice.exit()
        logger.error(error)
        raise error
        

RELAY_PIN = int(os.getenv('RELAY_PIN_1'))
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
logger.info(f'Final temperature,humidity:{format_LCD} Datetime: {current_time}')

if(int(final_temperature) <= 16):
    try:
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        GPIO.output(RELAY_PIN, GPIO.HIGH)
        logger.info(f'Toggled heater(relay_pin {RELAY_PIN}) ON.')
        setLCDMessage(format_LCD)
    except:
        logger.error(f'Failed to toggle relay ON!')
else:
    try:
        GPIO.setup(RELAY_PIN, GPIO.OUT)
        GPIO.output(RELAY_PIN, GPIO.LOW)
        logger.info(f'Toggled heater(relay_pin {RELAY_PIN}) OFF.')
        setLCDMessage(format_LCD)
    except:
        logger.error(f'Failed to toggle relay OFF!')

print("\nFinished - datetime:", datetime.now(), "\n")
