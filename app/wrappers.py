from functools import wraps
from flask import request, jsonify
from .models.models import User
from app.db import Db, db_name


def json_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.json:
            v = f(*args, **kwargs)
        else:
            v = jsonify({'Status': 400, 'error': 'empty request'}), 400
        return v
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]
            key = User.decode_token(token)
            #if isinstance(key, int):
            if Db(db_name).get_user('userid', key)['user_type'] == 'admin':
                v = f(*args, **kwargs)
            else:
                return jsonify(
                        {'msg': 'this action requores admin previledges'}
                        ), 403
            #else:
             #   v = jsonify({'msg': User.decode_token(token)}), 401
        else:
            v = jsonify({'msg': 'please login or signup'}), 401
        return v
    return decorated_function


def auth_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if auth_header:
            token = auth_header.split(" ")[1]
            key = User.decode_token(token)
            if isinstance(key, int):
                v = f(*args, **kwargs)
            else:
                v = jsonify(
                    {'Status': 401, 'error': User.decode_token(token)}
                    ), 401
        else:
            v = jsonify({'Status': 401, 'error': 'please login'}), 401
        return v
    return decorated_function
