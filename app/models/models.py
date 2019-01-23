from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash


class RedFlag:
    def __init__(self, red_flag_id, location, createdBy, title):
        self.red_flag_id = red_flag_id
        self.location = location
        self.createdBy = createdBy
        self.title = title


class User:
    def __init__(self, userid, name, email, password, user_type='user'):
        self.userid = userid
        self.name = name
        self.email = email
        self.password = password
        self.user_type = user_type

    def __repr__(self):
        return 'id: {}, user: {}, email: {}, user_type: {}'.format(
            self.userid, self.name, self.email, self.user_type)

    def set_password(self, password):
        return generate_password_hash(password)

    def validate_password(self, password):
        password_hash = db.fetch_user_name(self.name)['password_hash']
        return check_password_hash(password_hash, password)

    def generate_token(self):
        userid = self.userid
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(
                    minutes=125),
                'iat': datetime.utcnow(),
                'sub': userid
                }
            token = jwt.encode(
                payload,
                'trying',
                algorithm='HS256',
                )
            return token
        except Exception as error:
            print('error in token:', error)

    def renew_token(self, token):
        if self.decode_token(token)['exp'] < datetime.utcnow()\
                + timedelta(minutes=1):
            return self.generate_token()
        else:
            return token

    @staticmethod
    def decode_token(token):
        if db.check_token(token):
            result = 'please login'
        else:
            try:
                payload = jwt.decode(
                    token, 'trying', algorithms=['HS256'], verify=True)
                result = payload['sub']
            except jwt.ExpiredSignatureError:
                result = "Expired token. Please login to get a new token"
            except jwt.InvalidTokenError:
                result = "Invalid token. Please register or login"
            except Exception as error:
                print(error)
                result = error
        return result

    def dict_user(self):
        user = {}
        keys = ['userid', 'name', 'email', 'password_hash', 'user_type']
        try:
            for key in keys:
                user[key] = object.key
            return user
        except Exception as e:
            print(e)
