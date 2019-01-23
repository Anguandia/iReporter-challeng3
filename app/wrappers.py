from functools import wraps
from flask import request, jsonify


def json_required(f):

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.json:
            v = f(*args, **kwargs)
        else:
            v = jsonify({'Status': 400, 'error': 'empty request'}), 400
        return v
    return decorated_function
