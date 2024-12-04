from flask import (request, jsonify, Blueprint)
import RPi.GPIO as GPIO
from datetime import datetime, timedelta
import Adafruit_DHT
# from RPLCD.gpio import CharLCD
import re
import os
from dotenv import load_dotenv
import logging
from thingnet import rpi_controller as rpi_controller
from thingnet import water_pump as water_pump
from thingnet import dht11 as dht11

logger = logging.getLogger(__name__)

load_dotenv()

SENSOR = Adafruit_DHT.DHT11
DHT_PIN = int(os.getenv('DHT_GPIO_PIN'))

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/togglerelay', methods=['POST'])
def toggleRoute():
    if request.method == 'POST':
        ip = request.access_route[-1]
        choice = request.args.get('choice', None)
        relay_number = request.args.get('relay', None)
        res = rpi_controller.toggleRelay(ip, relay_number, choice)
        if(res):
            logger.info(f'IP:{ip} /togglerelay success. request:{request}')
            return jsonify({"status": f"Turned {choice} relay-{relay_number}",'ip': ip, }), 200

        logger.error(f'IP:{ip} /togglerelay failed. request:{request}')
        return jsonify({"error": f"Toggling relay failed.", 'ip': ip}), 400

@bp.route('/statusrelay', methods=['GET'])
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

@bp.route('/togglewaterpump', methods=['POST'])
def toggleRoute():
    if request.method == 'POST':
        ip = request.access_route[-1]
        run_time = request.args.get('run_time', None)
        relay_number = request.args.get('relay', None)
        number_of_retries = request.args.get('number_of_retries', None)
        res = water_pump.run_water_pump(relay_number, run_time, number_of_retries)
        if(res):
            logger.info(f'IP:{ip} /togglewaterpump success. request:{request}')
            return jsonify({"status": f"Water_pump runtime: {run_time}, number_of_retries: {number_of_retries}",'ip': ip, '_datetime': datetime.now()}), 200

        logger.error(f'IP:{ip} /togglewaterpump failed. request:{request}')
        return jsonify({"error": f"Toggling water_pump failed.", 'ip': ip}), 400

@bp.route('/temperature', methods=['GET'])
def getTemp():
    try:
        ip = request.access_route[-1]
        # humidity, temperature = Adafruit_DHT.read_retry(SENSOR, DHT_PIN)
        measurement = dht11.read_sensor(SENSOR, DHT_PIN)
        _formatTemperature = '{0:0.1f}*C'.format(measurement['temperature'])
        _formatHumidity = '{0:0.1f}%'.format(measurement['humidity'])
        rpi_controller.setLCDMessage(_formatTemperature, _formatHumidity)
        logger.info(f'IP:{ip} /temperature success. request:{request}')
        return jsonify({'temperature': measurement['temperature'], 'humidity': measurement['humidity'], 'format_temperature': _formatTemperature, 'format_humidity': _formatHumidity, '_datetime': datetime.now(), "ip": ip}), 200
    except:
        logger.error(f'IP:{ip} /temperature failed. request:{request}')
        return jsonify({'error': 'get temperature failed.', 'ip': ip}), 400

@bp.route('/getlogs', methods=['GET'])
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

        filtered_logs = rpi_controller.clean_logs(from_date, to_date, from_hour, to_hour)

        if(filtered_logs):
            logger.info(f'IP:{ip} /getlogs success. request:{request}')
            return jsonify(filtered_logs), 200

        logger.error(f'IP:{ip} /getlogs failed.')
        return jsonify({'error':'not found'}), 404
    except RuntimeError as e:
        logger.error(e)
