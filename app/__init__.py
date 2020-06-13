import yaml

from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect

from logging import config

from authlib.integrations.flask_client import OAuth
from config import app_config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'main.welcome'
moment = Moment()
bootstrap = Bootstrap()
csrf = CSRFProtect()

oauth = OAuth()


def create_app(config_name='default'):
    """
    Starts up the Flask application based on the supplied configuration
    :param config_class: Configuration to start the app with
    :type config_class:
    :return: the Flask app
    :rtype:
    """
    app = Flask(__name__)
    app.config.from_object(app_config[config_name])
    app_config[config_name].init_app(app)

    with open("log_config.yaml", 'rt') as f:
        config_data = yaml.safe_load(f.read())
        config.dictConfig(config_data)

    app.logger.debug('starting the app')
    app.logger.info('starting the app')
    app.logger.warning('starting the app')
    app.logger.error('starting the app')

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)

    oauth.init_app(app)
    oauth.register(
        'auth0',
        client_id=app.config['AUTH0_CLIENT_ID'],
        client_secret=app.config['AUTH0_CLIENT_SECRET'],
        api_base_url=app.config['AUTH0_CLIENT_DOMAIN'],
        access_token_url=app.config['AUTH0_CLIENT_DOMAIN'] + '/oauth/token',
        authorize_url=app.config['AUTH0_CLIENT_DOMAIN'] + '/authorize',
        client_kwargs={
            'scope': 'openid profile email',
        },
    )
    oauth.register(
        'strava',
        client_id=app.config['STRAVA_CLIENT_ID'],
        client_secret=app.config['STRAVA_CLIENT_SECRET'],
        api_base_url=app.config['STRAVA_CLIENT_DOMAIN'],
        access_token_url=app.config['STRAVA_CLIENT_DOMAIN'] + '/oauth/token',
        authorize_url=app.config['STRAVA_CLIENT_DOMAIN'] + '/oauth/authorize',
        client_kwargs={
            'scope': 'read,activity:read,activity:write',
        },
    )

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    csrf.exempt(api_bp)
    from app.support import bp as support_bp
    app.register_blueprint(support_bp, url_prefix='/support')

    return app


from app import models
