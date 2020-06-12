from flask import render_template

from app.main import bp


@bp.route('/privacy', methods=['GET'])
def privacy():
    """
    shows the privacy page
    :return:
    :rtype:
    """
    return render_template('privacypolicy.html', title='Privacy Policy')


@bp.route('/disclaimer', methods=['GET'])
def disclaimer():
    """
    shows the disclaimer page
    :return:
    :rtype:
    """
    return render_template('disclaimer.html', title='Disclaimer')


@bp.route('/cookies', methods=['GET'])
def cookies():
    """
    shows the cookie page
    :return:
    :rtype:
    """
    return render_template('cookies.html', title='Cookies')
