import os
from flask import Flask
from config.config import app_config
from .db import Db, db_name


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    app.db = Db(db_name)
    from app.auth import bp, views
    app.register_blueprint(bp)
    from app.red_flags import red_flag_bp, views
    app.register_blueprint(red_flag_bp)

    return app


app = create_app(os.getenv('FLASK_ENV'))
