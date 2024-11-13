# project-iot - simple flask api

Minimal flask API for checking a temperature, toggle relays and getting a logs from it.

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
cp .env.example .env && nano .env
```

3. Install packages
```
pip install -r requirements.txt
```

4. Flask run
```
flask run
```
