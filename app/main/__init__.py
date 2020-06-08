import os
from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes

if os.getenv('FLASK_CONFIG') in ['development', 'testing']:
    bp.add_url_rule('/edit_profile', 'edit_profile', routes.edit_profile, methods=['GET', 'POST'])
