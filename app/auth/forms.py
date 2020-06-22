from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class StravaIntegrationForm(FlaskForm):
    """
    Defines the form to enable/disable strava integration for the user
    """
    is_integrated = BooleanField('Log to Strava')
    submit = SubmitField('Confirm')


class LoginForm(FlaskForm):
    """
    Defines the login form
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')
