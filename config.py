import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    # Flask specifics
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY') or 'you-will-never-guess'
    WTF_CSRF_SECRET_KEY = os.environ.get('CSRF_SECRET_KEY') or SECRET_KEY
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # details provided by Auth0 following registration of an app
    AUTH0_CLIENT_ID = os.environ.get('AUTH0_CLIENT_ID')
    AUTH0_CLIENT_SECRET = os.environ.get('AUTH0_CLIENT_SECRET')
    AUTH0_CLIENT_DOMAIN = os.environ.get('AUTH0_CLIENT_DOMAIN')

    # details provided by Strava following registration of an app
    STRAVA_CLIENT_ID = os.environ.get('STRAVA_CLIENT_ID') or ''
    STRAVA_CLIENT_SECRET = os.environ.get('STRAVA_CLIENT_SECRET') or ''
    STRAVA_CLIENT_DOMAIN = os.environ.get('STRAVA_CLIENT_DOMAIN') or 'http://www.strava.com'

    # toggles saving exercises to strava
    CALL_STRAVA_API = os.environ.get('CALL_STRAVA_API') or False

    # staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')


class TestingConfig(Config):
    CALL_STRAVA_API = False
    TESTING = True
    LIVESERVER_PORT = 8943
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'test_app.db')


class StagingConfig(Config):
    DEBUG = False
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('STAGING_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'stage_app.db')


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'prod_app.db')


app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'default': DevelopmentConfig
}
