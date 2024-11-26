from flask import Flask, request, jsonify
import RPi.GPIO as GPIO
from datetime import datetime, timedelta
import Adafruit_DHT
from RPLCD.gpio import CharLCD
from werkzeug.middleware.proxy_fix import ProxyFix
import re
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()
SENSOR = Adafruit_DHT.DHT11
DHT_PIN = int(os.getenv('DHT_GPIO_PIN'))
LOG_DIR = os.getenv('LOG_DIR')
FILE_NAME = os.getenv('FILE_NAME')

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

log_file = os.path.join(LOG_DIR, 'project-iot.log')
logging.basicConfig(filename=log_file, level=logging.INFO)

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

def clean_logs(directory, from_date, to_date, from_hour, to_hour):
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
    for filename in os.listdir(directory):
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
        pins_data=pinse,
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
        
    
# ROUTES
@app.route('/togglerelay', methods=['POST'])
def toggleRoute():
    if request.method == 'POST':
        ip = request.access_route[-1]
        choice = request.args.get('choice', None)
        relay_number = request.args.get('relay', None)
        res = toggleRelay(ip, relay_number, choice)
        if(res):
            logger.info(f'IP:{ip} /togglerelay success. request:{request}')
            return jsonify({"status": f"Turned {choice} relay-{relay_number}",'ip': ip}), 200

        logger.error(f'IP:{ip} /togglerelay failed. request:{request}')
        return jsonify({"error": f"Toggling relay failed.", 'ip': ip}), 400

@app.route('/statusrelay', methods=['GET'])
def statusRelay():
    try:
        ip = request.access_route[-1]
        relay_number = request.args.get('number', None)
        
        relay_dict = {}
        
        GPIO.setmode(GPIO.BOARD)
        relay_number = int(relay_number)
        if(relay_number > 0 and relay_number < 9):
            for i in range(1,relay_number + 1):
                try:
                    pin_var_name = f"RELAY_PIN_{i}"
                    RELAY_PIN = int(os.getenv(pin_var_name))
                    GPIO.setup(RELAY_PIN, GPIO.OUT)
                    input_value = GPIO.input(int(RELAY_PIN))
                    relay_dict[f'relay_{i}_pin_{RELAY_PIN}'] = input_value
                except:
                    logger.error('Wrong number of relays provided.')
                    break
        
            logger.info(f'IP:{ip} /statusrelay success. relay_dict: {relay_dict} request:{request}')
            return jsonify({"status": relay_dict ,'ip': ip}), 200
        
        logger.error(f'IP:{ip} /statusrelay failed. request:{request}')
        return jsonify({'error': 'Something went wrong!', 'ip': ip}), 400
    except:
        logger.error(f'IP:{ip} Get relay status failed. request:{request}')
        return jsonify({'error': f'Status relay failed.', 'ip': ip}), 400

@app.route('/temperature', methods=['GET'])
def getTemp():
    try:
        ip = request.access_route[-1]
        humidity, temperature = Adafruit_DHT.read_retry(SENSOR, DHT_PIN)
        _formatTemperature = '{0:0.1f}*C'.format(temperature)
        _formatHumidity = '{0:0.1f}%'.format(humidity)
        setLCDMessage(_formatTemperature, _formatHumidity)
        logger.info(f'IP:{ip} /temperature success. request:{request}')
        return jsonify({'temperature': temperature, 'humidity': humidity, 'format_temperature': _formatTemperature, 'format_humidity': _formatHumidity, '_datetime': datetime.now(), "ip": ip}), 200
    except:
        logger.error(f'IP:{ip} /temperature failed. request:{request}')
        return jsonify({'error': 'get temperature failed.', 'ip': ip}), 400

@app.route('/getlogs', methods=['GET'])
def getLogs():
    try:
        ip = request.access_route[-1]
        date_format = '%Y-%m-%d'
        pattern_str = r'^\d{4}-\d{2}-\d{2}$'
        from_date = request.args.get('from_date', datetime(2023,11,9).strftime(date_format))
        to_date = request.args.get('to_date', datetime.now().strftime(date_format))
        from_hour = int(request.args.get('from_hour', 0))
        to_hour = int(request.args.get('to_hour', 23))

        if to_date is None:
            return jsonify({"error":"to_date is required."}), 406
        if not (0 <= from_hour <= 23 and 0 <= to_hour <= 23):
            return jsonify({"error": "Invalid hour format. Hours must be between 0 and 23."}), 400

        if re.match(pattern_str, from_date) and re.match(pattern_str, to_date):
            logger.info(f'IP:{ip} from_date:{from_date} & to_date:{to_date} VALIDATED SUCCESS')
        else:
            logger.error(f'IP:{ip} from_date:{from_date} & to_date:{to_date} VALIDATED FAILED!')
            return jsonify({'error': 'from_date not valid'}), 400

        filtered_logs = clean_logs(LOG_DIR, from_date, to_date, from_hour, to_hour)

        if(filtered_logs):
            logger.info(f'IP:{ip} /getlogs success. request:{request}')
            return jsonify(filtered_logs), 200

        logger.error(f'IP:{ip} /getlogs failed.')
        return jsonify({'error':'not found'}), 404
    except RuntimeError as e:
        logger.error(e)
