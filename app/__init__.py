from flask import Flask
from flask_cors import CORS
from flask_executor import Executor
from .config import Config
from .api import api_bp,api_hc
import os


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.executor = Executor()
    app.config.from_object(Config)
    if not(os.path.exists(os.path.abspath('/app/images'))):
        os.makedirs(os.path.abspath('/app/images'))
    if not(os.path.exists(os.path.abspath('/app/models'))):
        os.makedirs(os.path.abspath('/app/models'))
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    app.register_blueprint(api_hc)
    app.executor.init_app(app)
    return app
