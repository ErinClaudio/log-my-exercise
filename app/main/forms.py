from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, DecimalField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, AnyOf, Optional

from app.main import VALID_ACTIVITIES, SELECT_ACTIVITIES


class ActivityForm(FlaskForm):


    title = StringField('Title *', validators=[DataRequired(), Length(min=0, max=50)])
    motivation = TextAreaField('Reason for goal (optional)', validators=[Length(min=0, max=300)])
    reward = TextAreaField('Reward for achieving goal (optional)', validators=[Length(min=0, max=300)])
    description = TextAreaField('Description (optional)', validators=[Length(min=0, max=300)])
    activity_type = SelectField('Type *', choices=SELECT_ACTIVITIES, validators=[AnyOf(VALID_ACTIVITIES)])
    duration = IntegerField('Duration (mins) *',
                            validators=[DataRequired(),
                                        NumberRange(0, 999, message="Please enter a number between 0 and 999")])
    distance = DecimalField('Distance km (optional)', places=2,
                            validators=[Optional(),
                                        NumberRange(0, 1000, message="Please enter a number between 0 and 999")])
    user_tz = HiddenField(default='UTC', validators=[DataRequired()])
    submit = SubmitField('Save')
