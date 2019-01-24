import os


class Config:
    DEBUG = False
    CSRF_ENABLED = True


class Development(Config):
    DEBUG = True
    red_flags = {}


class Testing(Config):
    TESTING = True
    DEBUG = True
    red_flags = {}


class Production(Config):
    DEBUG = False
    TESTING = False
    DDATABASE_URL = 'postgres://zkmhjcntzlzigm:5e1a4dfe4ad76421fc92b9e702f6fb043b4e929767454258195955f2067bee43@ec2-107-21-224-76.compute-1.amazonaws.com:5432/dds37pk9ppk31q'


app_config = {
    'DEVELOPMENT': Development, 'TESTING': Testing, 'PRODUCTION': Production
    }
