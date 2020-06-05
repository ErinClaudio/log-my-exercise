from flask import render_template, flash, redirect, url_for, current_app
from flask_login import current_user, login_user, logout_user
from six.moves.urllib.parse import urlencode

from app import db, oauth
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User

INDEX_PAGE = 'main.index'


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Allows a user to log into the application
    :return: the template to render
    :rtype:
    """
    if current_user.is_authenticated:
        return redirect(url_for(INDEX_PAGE))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        # going to ignore any next querystring parameter and just send all users to the index page
        return redirect(url_for(INDEX_PAGE))

    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    """
    logs the user out of the application
    :return: the template to render
    :rtype:
    """
    logout_user()
    return redirect(url_for(INDEX_PAGE))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """
    allows a new user to register with the application
    :return: the template to render
    :rtype:
    """
    if current_user.is_authenticated:
        return redirect(url_for(INDEX_PAGE))
    add_user = True
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form, add_user=add_user)


@bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    """
    Allows a user to sign-up for an account, renders a simple page
    which then sends them to Auth0
    :return:
    :rtype:
    """
    if current_user.is_authenticated:
        return redirect(url_for(INDEX_PAGE))
    redirect_uri = url_for('auth.oauth_callback', _external=True)
    # extra_params = {"screen_hint":"signup"}, shoudl be able to pass this in to authorize_redirect but it errors
    return oauth.auth0.authorize_redirect(redirect_uri)


@bp.route('/authorize')
def oauth_authorize():
    """
    Calls auth0 to authorize the user
    :param provider: name of the provider, only auth0 is supported
    :type provider: string
    :return: redirects to the auth0 website
    :rtype:
    """
    if not current_user.is_anonymous:
        return redirect(url_for(INDEX_PAGE))
    redirect_uri = url_for('auth.oauth_callback', _external=True)
    return oauth.auth0.authorize_redirect(redirect_uri)


@bp.route('/callback')
def oauth_callback():
    """
    is called back by auth0 when it has authenticated the user
    will subsequently log the user into the appplication
    if they don't have an User entry in the database then one will be created
    will also update username and email if these have changed
    since they last logged in
    :param provider: auth0 is the only supported valie
    :type provider: string
    :return:
    :rtype:
    """
    if not current_user.is_anonymous:
        return redirect(url_for('index'))

    # token is required for authentication
    token = oauth.auth0.authorize_access_token()
    resp = oauth.auth0.get('userinfo')
    user_info = resp.json()
    social_id = 'auth0$' + user_info['sub']
    username = user_info['name'].split('@')[0]
    email = user_info['email']

    if social_id is None:
        flash('Authentication failed')
        return redirect(url_for(INDEX_PAGE))
    user = User.query.filter_by(social_id=social_id).first()
    if not user:
        user = User(social_id=social_id, username=username, email=email)
        db.session.add(user)
        db.session.commit()
    login_user(user, True)

    # if the user has changed their username or email since they were last here, then need to update the db
    if user.username != username or user.email != email:
        current_user.username, current_user.email = username, email
        db.session.commit()

    return redirect(url_for(INDEX_PAGE))


@bp.route('login_new')
def login_new():
    """
    serves the login page that directs the user to auth0 for login
    :return:
    :rtype:
    """
    return render_template('auth/new_login.html', title='New Sign In')


@bp.route('logout_new')
def logout_new():
    """
    logs the user out of auth0 and this website
    calls auth0 to do the logout
    :return:
    :rtype:
    """
    logout_user()
    params = {
        'returnTo': url_for('main.welcome', _external=True),
        'client_id': current_app.config['AUTH0_CLIENT_ID']
    }
    return redirect(oauth.auth0.api_base_url + '/v2/logout?' + urlencode(params))
