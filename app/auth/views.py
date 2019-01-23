from flask import jsonify, request
from . import bp
from app import db, validation
from app.validation import Validation
# from app.wrappers import admin_required, auth_required


@bp.route('/signup', methods=['POST'])
def signup():
    data = request.json
    ans = Validation().validateSignup(data)
    return jsonify({'Status': ans[0], ans[1]: ans[2]}), ans[0]
