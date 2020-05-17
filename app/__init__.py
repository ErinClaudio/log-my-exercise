from flask import Flask
from flask_bootstrap import Bootstrap
from config import app_config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_moment import Moment


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.login'
moment = Moment()
bootstrap = Bootstrap()

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

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp,url_prefix='/auth')
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    return app

from app import models
