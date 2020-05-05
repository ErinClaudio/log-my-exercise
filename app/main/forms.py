from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, DateTimeField, \
    SelectField
from wtforms.validators import DataRequired, ValidationError, Length, NumberRange, AnyOf

from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    submit = SubmitField('Save')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username.')


class ActivityForm(FlaskForm):
    title = StringField('Title *', validators=[DataRequired(),Length(min=0, max=50)])
    description = TextAreaField('Description (optional)', validators=[Length(min=0, max=300)])
    activity_type = SelectField('Type *', choices=[('1', 'Workout'), ('2', 'Yoga')], validators=[AnyOf(['1','2'])])
    duration = IntegerField('Duration (mins) *', validators=[DataRequired(),NumberRange(0,999,message="Please enter a number between 0 and 999")])
    timestamp = DateTimeField('Date of Activity', default=datetime.today, validators=[DataRequired()])
    submit = SubmitField('Save')
