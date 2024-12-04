# thingnet - simple flask api

flask API for checking a temperature, toggle relays and getting a logs from it.

## requirements
- Rpi model 4B
- Python
    - important packages(without you cannot use DHT11 sensor and RPI pins): **Adafruit_DHT** & **Rpi.GPIO**
- Nginx(for deployment)

## how to start project locally
1. Create venv
```
python -m venv venv
```

2. Modify .env
```
cp thingnet/.env.example thingnet/.env && nano thingnet/.env
```

3. Create instance directory and adjust config.py and bash.cfg
```
mkdir instance && touch instance/config.py && touch instance/bash.cfg
```

4. Install packages
```
pip install -r requirements.txt
```

5. Flask run
```
flask run
```
