from flask import Blueprint

bp = Blueprint('inspires', __name__)

from app.inspires import routes, forms