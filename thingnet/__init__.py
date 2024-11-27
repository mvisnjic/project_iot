import os
from dotenv import load_dotenv
from flask import Flask, request
from werkzeug.middleware.proxy_fix import ProxyFix
import logging

load_dotenv()

LOG_DIR = os.getenv('LOG_DIR')

logger = logging.getLogger(__name__)

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    # )
    app.wsgi_app = ProxyFix(app.wsgi_app)
    
    if LOG_DIR is None:
        raise ValueError("LOG_DIR is not set in the environment variables.")
    
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    
    log_file = os.path.join(LOG_DIR, 'project-iot.log')
    logging.basicConfig(filename=log_file, level=logging.INFO)

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def hello():
        ip = request.access_route[-1]
        logger.info(f'IP:{ip} is FUCKED!')
        return f'Hey, {ip} fuck off!'

    from . import api
    app.register_blueprint(api.bp)
    
    logger.info('Created application success.')
    return app