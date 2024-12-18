import RPi.GPIO as GPIO
from datetime import datetime, timedelta
import Adafruit_DHT
from RPLCD.gpio import CharLCD
import re
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

LOG_DIR = os.getenv('LOG_DIR')
FILE_NAME = os.getenv('FILE_NAME')

def prepare_relay_and_get_input(relay_pin):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(relay_pin, GPIO.OUT)
    return GPIO.input(relay_pin)

def logging_relay(ip, relay_number, relay_pin, choice, before_input_val):
    logger.info(f'IP:{ip} toggling relay_{relay_number}_pin_{relay_pin} {choice}.')
    new_input_val = GPIO.input(relay_pin)
    logger.info(f'Relay current state:{new_input_val}, before state:{before_input_val}')
    
def toggleRelay(ip=-1, relay_number=-1, choice='off'):
    pin_var_name = f"RELAY_PIN_{relay_number}"
    RELAY_PIN = int(os.getenv(pin_var_name))
    if choice.upper() == 'ON':
        try:
            before_input_value = prepare_relay_and_get_input(RELAY_PIN)
            GPIO.output(RELAY_PIN, GPIO.HIGH)
            logging_relay(ip, relay_number, RELAY_PIN, choice, before_input_value)
            
            return True
        except:
            logger.error(f'IP:{ip} failed to toggle relay {choice}!')
            logger.error('RELAY_PIN', RELAY_PIN)
            return False
    elif choice.upper() == 'OFF':
        try:
            before_input_value = prepare_relay_and_get_input(RELAY_PIN)
            GPIO.output(RELAY_PIN, GPIO.LOW)
            logging_relay(ip, relay_number, RELAY_PIN, choice, before_input_value)
            return True
        except:
            logger.error(f'IP:{ip} failed to toggle relay {choice}!')
            return False
    else:
        logger.error(f'IP:{ip} choice error! choice: "{choice}"')
        return False


def clean_logs(from_date, to_date, from_hour, to_hour):
    log_pattern = r'Temp=(\d+\.\d+)\*C\s+Humidity=(\d+\.\d+)%\s+Datetime\s-\s([\d-]+\s[\d:.]+)'
    cleaned_logs = []

    from_datetime_str = f"{from_date} {from_hour}"
    to_datetime_str = f"{to_date} {to_hour}"

    from_date = datetime.strptime(from_date, '%Y-%m-%d')
    to_date = datetime.strptime(to_date, '%Y-%m-%d')
    from_datetime = datetime.strptime(from_datetime_str, '%Y-%m-%d %H')
    if(to_hour == 23):
        to_datetime = datetime.strptime(to_datetime_str, '%Y-%m-%d %H') + timedelta(hours=1) - timedelta(seconds=1)
    else:
        to_datetime = datetime.strptime(to_datetime_str, '%Y-%m-%d %H') + timedelta(minutes=30)

    from_timestamp = from_datetime.timestamp()
    to_timestamp = to_datetime.timestamp()

    last_measurement = {}
    for filename in os.listdir(LOG_DIR):
        if filename == FILE_NAME:
            with open(LOG_DIR + FILE_NAME, 'r') as file:
                for line in file:
                        match = re.match(log_pattern, line)
                        if match:
                            temperature = float(match.group(1))
                            humidity = float(match.group(2))
                            datetime_str = match.group(3)
                            datetime_formated = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S.%f')
                            timestamp = datetime_formated.timestamp()

                            if timestamp > to_timestamp:
                                break
                            if from_timestamp <= timestamp and to_timestamp >= timestamp:
                                _hour_key = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                                date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
                                time = datetime.fromtimestamp(timestamp).strftime('%H:%M')
                                last_measurement[_hour_key] = {
                                    'temperature': temperature,
                                    'humidity': humidity,
                                    'datetime_str': datetime_str,
                                    'date': date,
                                    'time': time,
                                    'timestamp': timestamp,
                                }

    cleaned_logs.extend(last_measurement.values())

    if(len(cleaned_logs) > 0):
        return cleaned_logs
    return False;

def setLCDMessage(temperature,humidity):
    PIN_RS = os.getenv('PIN_RS')
    PIN_RW = os.getenv('PIN_RW')
    PIN_E = os.getenv('PIN_E')
    PINS = os.getenv('PINS_DATA')
    
    pins = list(map(int, PINS.split(',')))
    
    try:
        lcd = CharLCD(
        pin_rs=int(PIN_RS),
        pin_rw=int(PIN_RW),
        pin_e=int(PIN_E),
        pins_data=pins,
        cols=16, rows=4,
        numbering_mode=GPIO.BOARD
        )
    
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M')
        lcd.clear()
        lcd.write_string(f"{temperature} {humidity}\r\n{current_time}")
    except:
        logger.error(f'Setting LCD message error.')
    finally:
        lcd.close(clear=False)
