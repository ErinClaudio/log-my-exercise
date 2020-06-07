import os
from flask import Blueprint

bp = Blueprint('auth', __name__)

from app.auth import routes, strava

if os.getenv('FLASK_CONFIG') in ['development', 'testing']:
    bp.add_url_rule('/login', 'login', routes.login, methods=['GET', 'POST'])
    bp.add_url_rule('/logout', 'logout', routes.logout)
    bp.add_url_rule('/register', 'register', routes.register, methods=['GET', 'POST'])
