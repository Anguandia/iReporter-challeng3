import psycopg2
import os
from app.models.models import RedFlag
import datetime
import uuid

user = os.getenv('USER', 'postgres')
password = os.getenv('PASSWORD', 'kukuer1210')
host = os.getenv('HOST', 'localhost')
db_name = os.getenv('DATABASE', 'irent')


class Db:
    def __init__(self, db_name):
        self.db_name = db_name
        try:
            self.connection = psycopg2.connect(
                f"dbname = postgres user = postgres password = kukuer1210 host = localhost \
                port = 5432"
                )
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            self.cursor.execute(f'''create database {self.db_name}''')
            self.connection.commit()
            self.cursor.close()
            self.connection.close()
            print(f'database {self.db_name} created')
        except Exception as e:
            print(e)
        self.connection = psycopg2.connect(
                f'''dbname = {self.db_name} user = {user} password = {password} host = {host} \
                port = 5432'''
                )
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()
        try:
            create_red_flags = 'CREATE TABLE IF NOT EXISTS red_flags(\
                    red_flag_id INT UNIQUE NOT NULL, comment VARCHAR\
                    NOT NULL, createdBy INT NOT NULL, createdOn DATE NOT NULL,\
                    images VARCHAR ARRAY, location VARCHAR NOT NULL, status\
                    VARCHAR NOT NULL, title VARCHAR NOT NULL, videos VARCHAR\
                    ARRAY\
                    )'
            self.cursor.execute(create_red_flags)
            self.save()
            print('table red_flags created')
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def save(self):
        self.connection.commit()

    def create(self, data):
        others = {
            'status': 'draft', 'videos': '{}', 'images': '{}',
            'comment': ''}
        long = int(uuid.uuid4())
        id = str(long)[:4] + str(long)[-4:]
        red_flag = RedFlag(
            int(id), data['location'], data['createdBy'],
            data['title']
            )
        red_flag.__setattr__('createdOn', datetime.datetime.now())
        for key in others:
            if key in data:
                red_flag.__setattr__(key, data[key])
            else:
                red_flag.__setattr__(key, others[key])
        try:
            create_red_flag_query = '''INSERT INTO red_flags (
                red_flag_id, comment, createdBy, createdOn, images, location,\
                status, title, videos) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
            self.cursor.execute(
                create_red_flag_query, (
                    red_flag.red_flag_id, red_flag.comment, red_flag.createdBy,
                    red_flag.createdOn, red_flag.images, red_flag.location,
                    red_flag.status,
                    red_flag.title, red_flag.videos
                    ))
            self.save()
            print("red_flag", red_flag.__dict__, "saved to db")
            return [
                    201, 'data', [{
                        'id': red_flag.red_flag_id,
                        'message': 'Created red flag'
                        }]
                ]
        except (Exception, psycopg2.IntegrityError) as error:
            print("Failed to create red_flag:", error)
            res = [500, 'error', str(error)]
        return res

    def get_red_flags(self):
        try:
            self.cursor.execute(
                "SELECT * FROM red_flags ORDER BY createdOn DESC"
                )
            flags = self.cursor.fetchall()
            red_flags = [Db.dict_red_flag(red_flag) for red_flag in flags]
            res = res = [200, 'data', red_flags]
        except Exception as error:
            print(error)
            res = [500, 'error', 'internal error, please contact support']
        return res

    def get_red_flag(self, red_flag_id):
        try:
            self.cursor.execute((
                "SELECT * FROM red_flags WHERE red_flag_id = %s"),
                (red_flag_id,))
            red_flag = self.cursor.fetchone()
            res = [200, 'data', [self.dict_red_flag(red_flag)]]
        except Exception as error:
            print(error)
            res = [500, 'error', 'internal error, please contact support']
        return res

    def edit(self, red_flag_id, data, field):
        flag = self.get_red_flag(red_flag_id)[2][0]
        if field == 'location' and 'geolocation' not in flag[
                'location']:
            value = flag['location'] + ' ' + data['location']
            res = 'added'
        elif field == 'location' and 'geolocation' in flag['location']:
            value =\
                    flag['location'][:flag['location'].index(
                        'geolocation')] + data['location']
            res = 'updated'
        else:
            value = data
            res = 'updated'
        if field == 'comment':
            sql_update_query = 'UPDATE red_flags SET comment = %s WHERE\
            red_flag_id = %s'
        elif field == 'location':
            sql_update_query = 'UPDATE red_flags SET location = %s WHERE\
            red_flag_id = %s'
        else:
            sql_update_query = 'UPDATE red_flags SET status = %s\
                WHERE red_flag_id = %s'
        self.cursor.execute(sql_update_query, (value, red_flag_id))
        self.save()
        return [200, 'data', [{
                'id': int(red_flag_id), 'message':
                f'{res} red-flag record\'s {field}'}]]

    def delete_red_flag(self, red_flag_id):
        try:
            sql_delete_query = 'delete from red_flags WHERE red_flag_id = %s'
            self.cursor.execute(sql_delete_query, (red_flag_id,))
            self.save()
            res = [200, 'data', [{'id': int(red_flag_id), 'message':
                                 'red-flag record has been deleted'}]]
        except KeyError:
            res = [404, 'error', 'red flag not found']
        except (Exception, psycopg2.DatabaseError) as error:
            res = [500, 'error', 'internal error, please contact support']
            print("Error deleting", error)
        print(res)
        return res

    @staticmethod
    def dict_red_flag(tup):
        red_flag = {}
        keys = ['red_flag_id', 'comment', 'createdBy', 'createdOn', 'images',
                'location', 'status', 'title', 'videos']
        try:
            for key in keys:
                red_flag[key] = tup[keys.index(key)]
            return red_flag
        except Exception as e:
            print(e)
