from flask import render_template, flash, redirect, url_for
from flask import request
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from flask import current_app

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
