from flask import Blueprint

bp = Blueprint('goal', __name__)

from app.goal import routes, forms
