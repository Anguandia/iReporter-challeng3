import datetime
from .db import Db, db_name


class Validation:
    data_types = {
        'id': int,
        'createdOn': datetime.datetime,
        'createDby': int,
        'type': str,
        'location': str,
        'status': str,
        'comment': str
        }

    def bad_type(self, data):
        res = None
        for field in data:
            if field in self.data_types and not isinstance(
                    data[field], self.data_types[field]):
                res = [
                    400, 'error',
                    f'{field} should be of type {self.data_types[field]}'
                    ]
            elif field in ['images', 'videos']:
                res = self.validate_pictures(data[field])
        if res:
            return res

    def validate_pictures(self, pics):
        for pic in pics:
            if not isinstance(pic, str):
                return [
                    400, 'error',
                    f"'{pic}' image path should be a string"
                    ]

    def validate_route(self, resource):
        if resource != 'red_flags':
            res = [400, 'error', f'wrong url, check \'{resource}\'']
            return res

    def validate_basics(self, data):
        for field in ['location', 'comment', 'createdBy', 'title']:
            if field not in data:
                return [
                    400, 'error',
                    f'{field} field missing, invalid key or incorrect'
                    ]
            elif not data[field]:
                return [400, 'error', 'please submit {}'.format(field)]

    def validate_duplicate(self, data):
        flags = Db(db_name).get_red_flags()[2]
        for flag in flags:
            if data['location'] in flag['location'] and data['title']\
                    == flag['title']:
                return [
                    200, 'data', [
                        {'id': flag['red_flag_id'],
                         'message': 'red flag exists'}
                        ]
                    ]

    def validate_descriptive(self, data):
        for field in ['location', 'comment', 'title']:
            if field and not self.validate_int(
                    data[field]):
                return [
                    400, 'error', f'{field} must be descriptive'
                    ]

    def validate_new(self, data):
        if self.validate_basics(data):
            result = self.validate_basics(data)
        elif self.validate_descriptive(data):
            result = self.validate_descriptive(data)
        elif self.bad_type(data):
            result = self.bad_type(data)
        elif self.validate_duplicate(data):
            result = self.validate_duplicate(data)
        else:
            result = Db(db_name).create(data)
        return result

    def validate_int(self, value):
        try:
            int(value)
        except ValueError:
            return 'id must be a number'

    def validate_edit(self, data, red_flag_id, field):
        if self.validate_field(field):
            result = self.validate_field(field)
        elif self.validate_editable(red_flag_id):
            result = self.validate_editable(red_flag_id)
        elif self.validate_data(field, data):
            result = self.validate_data(field, data)
        elif field == 'status' and self.validate_status(data):
            result = self.validate_status(data)
        elif field == 'location':
            result = self.validate_geoloc(red_flag_id, data)
        else:
            result = Db(db_name).edit(red_flag_id, data[field], field)
        return result

    def validate_status(self, data):
        if data['status'] not in [
                'under investigation', 'resolved', 'rejected']:
            return [400, 'error', 'invalid status']

    '''to be editable, target must exist and not be in status 'resolved' or
    'rejected'''
    def validate_editable(self, id):
        # initialize return value to none
        ret = None
        # check if update target is available
        flag = Db(db_name).get_red_flag(id)[2]
        if flag == [None]:
            ret = [404, 'error', 'red flag not found']
        # check if target is not resolved or rejected
        elif flag[0]['status'] in ['resolved', 'rejected']:
            ret = [
                403, 'error', f'red flag already {flag[0]["status"]}'
                ]
        return ret

    # check if end point specified correctly
    def validate_field(self, field):
        if field not in ['location', 'comment', 'status']:
            return [400, 'error', f'wrong endpoint \'{field}\'']

    def validate_data(self, field, data):
        if field not in data:
            result = [
              400, 'error',
              f'{field} key missing, check your input or url'
              ]
        # safeguard against accidental deleting of field data
        elif not data[field]:
            result = [400, 'error', f'submit new {field}']
        else:
            result = None
        return result

    def validate_geoloc(self, red_flag_id, data):
        d = data['location'].split(',')
        if ',' not in data['location']:
            result = [
                400, 'error',
                "location must be of format'latitude <comma> longitude'"
                ]
        elif self.validate_geoloc_type(d):
            result = self.validate_geoloc_type(d)
        else:
            result = Db(db_name).edit(red_flag_id, {
                'location': 'geolocation ' + f'N: {d[0]}, E: {d[1]}'},
                'location')
        return result

    def validate_geoloc_type(self, goeloc):
        try:
            [float(i) for i in goeloc]
        except ValueError:
            return [400, 'error', 'coordinates must be floats']

    def validate_signup(self, data):
        if self.validate_signup_data(data):
            res = self.validate_signup_data(data)
        elif Db(db_name).get_user('email', data['email']):
            res = [403, 'error', 'account already exists, please login']
        elif Db(db_name).get_user('name', data['name']):
            res = [409, 'error', 'name conflict, use a different name']
        elif self.validate_password(data['password']):
            res = self.validate_password(data['password'])
        elif self.validate_email(data['email']):
            res = self.validate_email(data['email'])
        elif self.validate_name(data['name']):
            res = self.validate_name(data['name'])
        else:
            res = Db(db_name).signup(data)
        return res

    def validate_signup_data(self, data):
        for key in ['name', 'email', 'password']:
            res = None
            if key not in data:
                res = f'{key} key missing or incorrect'
            elif not data[key]:
                res = f'please fill in {key}'
            if res:
                return [400, 'error', res]

    def validate_password(self, password):
        if len(password) not in range(6, 13):
            res = 'password must be to 12 characters long'
        elif not any(i.islower() for i in password):
            res = 'password must have atleast one lowercase'
        elif not any(i.isupper() for i in password):
            res = 'password must have atleast one uppercase'
        elif not any(i.isdigit() for i in password):
            res = 'password must have atleast one digit'
        elif not set('!@#$%&*') & set(password):
            res = 'password must have atleast one special character'
        else:
            res = None
        if res:
            return [400, 'error', res]

    def validate_email(self, email):
        required = ['@', '.']
        res = None
        if not set(required) & set(email) == set(required):
            res = 'invalid email format'
        elif not 0 < email.index('@') < (email.rindex('.') - 2) < (
                    len(email) - 3):
            res = 'double check your email'
        if res:
            return [400, 'error', res]

    def validate_name(self, name):
        if len(name) > 25:
            return [400, 'error', 'name must be utmost 25 characters long']

    def validate_login(self, data):
        if self.validate_login_data(data):
            res = self.validate_login_data(data)
        elif not self.validate_email(data['identity']):
            res = Db(db_name).check_user(data, 'email')
        else:
            res = Db(db_name).check_user(data, 'name')
        return res

    def validate_login_data(self, data):
        for key in ['identity', 'password']:
            res = None
            if key not in data:
                res = f'{key} key missing'
            elif not data[key]:
                res = f'please provide {key} value'
            if res:
                return [400, 'error', res]
