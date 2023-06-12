from flask import Flask
from flask import request
import time
from flask import jsonify 
import RPi.GPIO as GPIO
from datetime import datetime
import Adafruit_DHT
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

# pin of the relay
relayPin = 11
# DHT-11 temp sensor
sensor = Adafruit_DHT.DHT11
dhtPin = 24

def toggle(isOpened=False):
    if(isOpened):
        print("ON")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(relayPin, GPIO.OUT)
        GPIO.output(relayPin, GPIO.HIGH)
        return isOpened
    else:
        print("OFF")
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(relayPin, GPIO.OUT)
        GPIO.output(relayPin, GPIO.LOW)
        return isOpened

@app.route('/turn-on', methods=['GET', 'POST'])
def turnOn():
    if request.method == 'POST':
        toggle(True)
        return jsonify({"success": "Turned on light"}), 200
        # return "Turned on light"
    else:
        return jsonify(error="error"), 404

@app.route('/turn-off', methods=['GET', 'POST'])
def turnOff():
    if request.method == 'POST':
        toggle(False)
        return jsonify({"success": "Turned off light"}), 200     
        # return "Turned off light"
    else:
        return jsonify(error="error"), 404
    
@app.route('/temperature', methods=['GET'])
def getTemp():
    humidity, temperature = Adafruit_DHT.read_retry(sensor, dhtPin)
    _formatTemperature = '{0:0.1f}*C'.format(temperature)
    _formatHumidity = '{0:0.1f}%'.format(humidity)
    return jsonify({"success": {"temperature": _formatTemperature, "humidity": _formatHumidity, "_datetime": datetime.now()}}), 200     
