import os

from flask import Blueprint

bp = Blueprint('main', __name__)
ACTIVITIES_LOOKUP = {1: 'Workout', 2: 'Yoga', 3: 'Bicycle Ride', 4: 'Run', 5: 'Walk'}
ICONS_LOOKUP = {1: "fas fa-dumbbell", 2: "fas fa-spa", 3: "fas fa-biking", 4: "fas fa-running", 5: "fas fa-shoe-prints",
                6: "fas fa-swimmer"}

from app.main import routes

if os.getenv('FLASK_CONFIG') in ['development', 'testing']:
    bp.add_url_rule('/edit_profile', 'edit_profile', routes.edit_profile, methods=['GET', 'POST'])
