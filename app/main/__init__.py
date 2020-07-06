import os

from flask import Blueprint

bp = Blueprint('main', __name__)
ACTIVITIES_LOOKUP = {1: 'Workout', 2: 'Yoga', 3: 'Bicycle Ride', 4: 'Run', 5: 'Walk', 6: 'Swimming'}
ICONS_LOOKUP = {1: "fas fa-dumbbell", 2: "fas fa-spa", 3: "fas fa-biking", 4: "fas fa-running", 5: "fas fa-shoe-prints",
                6: "fas fa-swimmer"}

VALID_ACTIVITIES = [str(i) for i in ACTIVITIES_LOOKUP.keys()]
SELECT_ACTIVITIES = sorted([(str(a), b) for a, b in list(ACTIVITIES_LOOKUP.items())])

from app.main import routes
