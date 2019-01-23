from flask import Flask
from config.config import app_config
from .db import Db, db_name


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    app.db = Db(db_name)

    return app
