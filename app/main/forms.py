from operator import itemgetter

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, DecimalField
from wtforms.validators import DataRequired, ValidationError, Length, NumberRange, AnyOf, Optional

from app.main import ACTIVITIES_LOOKUP
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
    valid_activities = [str(i) for i in ACTIVITIES_LOOKUP.keys()]
    select_activities = sorted([(str(a), b) for a, b in list(ACTIVITIES_LOOKUP.items())])

    title = StringField('Title *', validators=[DataRequired(), Length(min=0, max=50)])
    description = TextAreaField('Description (optional)', validators=[Length(min=0, max=300)])
    activity_type = SelectField('Type *', choices=select_activities, validators=[AnyOf(valid_activities)])
    duration = IntegerField('Duration (mins) *',
                            validators=[DataRequired(),
                                        NumberRange(0, 999, message="Please enter a number between 0 and 999")])
    distance = DecimalField('Distance km (optional)', places=2,
                            validators=[Optional(),
                                        NumberRange(0, 1000, message="Please enter a number between 0 and 999")])
    submit = SubmitField('Save')
