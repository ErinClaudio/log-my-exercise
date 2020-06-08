from flask import render_template
from app.errors import bp
from app import db


@bp.app_errorhandler(403)
def forbidden(error):
    """
    shown when access is forbidden error
    """
    return render_template('errors/403.html'), 403


@bp.app_errorhandler(404)
def not_found_error(error):
    """
    shown on a 404 page not found error
    """
    return render_template('errors/404.html'), 404


@bp.app_errorhandler(500)
def internal_error(error):
    """
    shown on a general error
    """
    db.session.rollback()
    return render_template('errors/500.html'), 500
