from flask import jsonify, request
from . import bp
from app.validation import Validation
# from app.wrappers import admin_required, auth_required


@bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    resp = Validation().validate_signup(data)
    return display(resp)


@bp.route('/login', methods=['POST'])
def login():
    data = request.json
    resp = Validation().validate_login(data)
    return display(resp)


def display(resp):
    return jsonify({'Status': resp[0], resp[1]: resp[2]}), resp[0]
