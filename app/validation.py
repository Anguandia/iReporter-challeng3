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
                res = self.validatePictures(data[field])
        if res:
            return res

    def validatePictures(self, pics):
        for pic in pics:
            if not isinstance(pic, str):
                return [
                    400, 'error',
                    f"'{pic}' image path should be a string"
                    ]

    def validateRoute(self, resource):
        if resource != 'red_flags':
            res = [400, 'error', f'wrong url, check \'{resource}\'']
            return res

    def validateBasics(self, data):
        for field in ['location', 'comment', 'createdBy', 'title']:
            if field not in data:
                return [
                    400, 'error',
                    f'{field} field missing, invalid key or incorrect'
                    ]
            elif not data[field]:
                return [400, 'error', 'please submit {}'.format(field)]

    def validateDuplicate(self, data):
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

    def validateDescriptive(self, data):
        for field in ['location', 'comment', 'title']:
            if field and not self.validateInt(
                    data[field]):
                return [
                    400, 'error', f'{field} must be descriptive'
                    ]

    def validateNew(self, data):
        if self.validateBasics(data):
            result = self.validateBasics(data)
        elif self.validateDescriptive(data):
            result = self.validateDescriptive(data)
        elif self.bad_type(data):
            result = self.bad_type(data)
        elif self.validateDuplicate(data):
            result = self.validateDuplicate(data)
        else:
            result = Db(db_name).create(data)
        return result

    def validateInt(self, value):
        try:
            int(value)
        except ValueError:
            return 'id must be a number'

    def validateEdit(self, data, red_flag_id, field):
        if self.validateField(field):
            result = self.validateField(field)
        elif self.validateEditable(red_flag_id):
            result = self.validateEditable(red_flag_id)
        elif self.validateData(field, data):
            result = self.validateData(field, data)
        elif field == 'status' and self.validateStatus(data):
            result = self.validateStatus(data)
        elif field == 'location':
            result = self.validateGeoloc(red_flag_id, data)
        else:
            result = Db(db_name).edit(red_flag_id, data[field], field)
        return result

    def validateStatus(self, data):
        if data['status'] not in [
                'under investigation', 'resolved', 'rejected']:
            return [400, 'error', 'invalid status']

    '''to be editable, target must exist and not be in status 'resolved' or
    'rejected'''
    def validateEditable(self, id):
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
    def validateField(self, field):
        if field not in ['location', 'comment', 'status']:
            return [400, 'error', f'wrong endpoint \'{field}\'']

    def validateData(self, field, data):
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

    def validateGeoloc(self, red_flag_id, data):
        d = data['location'].split(',')
        if ',' not in data['location']:
            result = [
                400, 'error',
                "location must be of format'latitude <comma> longitude'"
                ]
        elif self.validateGeolocType(d):
            result = self.validateGeolocType(d)
        else:
            result = Db(db_name).edit(red_flag_id, {
                'location': 'geolocation ' + f'N: {d[0]}, E: {d[1]}'},
                'location')
        return result

    def validateGeolocType(self, goeloc):
        try:
            [float(i) for i in goeloc]
        except ValueError:
            return [400, 'error', 'coordinates must be floats']

    def validateSignup(self, data):
        name = data['name']
        email = data['email']
        password = data['password']
        if self.validateKeys(data):
            res = self.validateKeys(data)
        elif self.validateValues(data):
            res = self.validateValues(data)
        elif Db(db_name).get_user_email(email):
            res = [403, 'error', 'account already exists, please login']
        elif Db(db_name).get_user_name(name):
            res = [409, 'error', 'name conflict, use a different name']
        elif self.validatePassword(password):
            res = self.validatePassword(password)
        elif self.validateEmail(email):
            res = self.validateEmail(email)
        elif self.validateName(name):
            res = self.validateName(name)
        else:
            res = Db(db_name).signup(data)
        return res

    def validateKeys(self, data):
        for key in ['name', 'email', 'password']:
            if key not in data:
                return [400, 'error', f'{key} key missing or incorrect']

    def validateValues(self, data):
        for field in data:
            if not data[field]:
                return [400, 'error', f'please fill in {field}']

    def validatePassword(self, password):
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

    def validateEmail(self, email):
        required = ['@', '.']
        if not set(required) & set(email) == set(required):
            res = [400, 'error', 'invalid email format']
            a = email.index('@')
            b = email.rindex('.')
        elif not 0 < email.index('@') < (email.rindex('.') - 2) < (
                    len(email) - 3):
            res = [400, 'error' 'double check your email']
        else:
            res = None
        return res

    def validateName(self, name):
        if len(name) > 25:
            return [400, 'error', 'name must be utmost 25 characters long']
