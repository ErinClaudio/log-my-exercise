
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo

from app.models import User


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


class RegistrationForm(FlaskForm):
    """
    Defines a form to register a new user
    """
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password',
                              validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """
        Validates uniqueness of the username. Raises a ValidationError if it's not unique
        :param username: the proposed username
        :type username: string
        :return:
        :rtype:
        """
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        """
        Validates uniqueness of the email address. Raised a ValidationError if it's not unique
        :param email: the proposed email address
        :type email: string
        :return:
        :rtype:
        """
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address')
