import os
from flask import Blueprint

bp = Blueprint('main', __name__)
ACTIVITIES_LOOKUP = {1: 'Workout', 2: 'Yoga', 3: 'Bicycle Ride', 4: 'Run', 5: 'Walk'}

from app.main import routes

if os.getenv('FLASK_CONFIG') in ['development', 'testing']:
    bp.add_url_rule('/edit_profile', 'edit_profile', routes.edit_profile, methods=['GET', 'POST'])
