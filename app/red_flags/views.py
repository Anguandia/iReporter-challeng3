from flask import request, jsonify
from app.db import Db, db_name
from app.validation import Validation
from app.wrappers import *
from . import red_flag_bp


@red_flag_bp.route('/')
def home():
    return jsonify({
      'create or get all flags':
      'api/v1/red_flags',
      'get or delete single flag':
      'api/v1/red_flags/id',
      'edit flag': 'api/v1/red_flags/id/field'
      })


@red_flag_bp.route('/<resource>', methods=['GET', 'POST', 'PATCH', 'DELETE'])
@red_flag_bp.route(
  '/<resource>/<id>', methods=['GET', 'POST', 'PATCH', 'DELETE']
  )
@red_flag_bp.route(
  '/<resource>/<id>/<action>',
  methods=['GET', 'POST', 'PATCH', 'DELETE']
  )
def wrongURL(resource, methods=[], id=None, action=None):
    if request.method not in methods:
        res = [405, 'error', 'wrong method']
    return result(res)


@red_flag_bp.route('/red_flags', methods=['POST'])
@auth_required
@json_required
def create_flag():
    token = request.headers.get('Authorization').split(' ')[1]
    data = request.json
    data['token'] = str(token)
    return result(Validation().validate_new(data))


@red_flag_bp.route('/red_flags', methods=['get'])
def get_flags():
    return result(Db(db_name).get_red_flags())


@red_flag_bp.route('/red_flags/<red_flag_id>', methods=[
    'get', 'delete'])
def single_flag(red_flag_id):
    if Validation().validate_int(red_flag_id):
        res = [400, 'error', Validation().validate_int(red_flag_id)]
    elif request.method == 'GET':
        res = Db(db_name).get_red_flag(red_flag_id)
    elif request.method == 'DELETE':
        res = Db(db_name).delete_red_flag(red_flag_id)
    return result(res)


@red_flag_bp.route('/red_flags/<red_flag_id>/<key>', methods=[
    'patch'])
@json_required
def edit(red_flag_id, key):
    data = request.json
    res = Validation().validate_edit(data, red_flag_id, key)
    return result(res)


@red_flag_bp.route('/red_flags/<red_flag_id>/status', methods=[
    'patch'])
@admin_required
@json_required
def update_status(red_flag_id, key='status'):
    data = request.json
    res = Validation().validate_edit(data, red_flag_id, 'status')
    return result(res)



def result(res):
    return jsonify({'Status': res[0], res[1]: res[2]}), res[0]
