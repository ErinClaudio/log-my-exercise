from datetime import datetime, timedelta

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, IntegerField, SelectField, DecimalField, HiddenField, \
    DateTimeField
from wtforms.validators import DataRequired, Length, NumberRange, AnyOf, Optional, ValidationError

from app.main import VALID_ACTIVITIES, SELECT_ACTIVITIES


class ActivityForm(FlaskForm):
    """
    Represents a regular activity
    """
    title = StringField('Title *', validators=[DataRequired(), Length(min=0, max=50)])
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


class CompletedActivity(ActivityForm):
    """
    Represents a completed activity occuring at a specific date/time
    """
    timestamp = DateTimeField('Date Completed *', format='%d/%m/%Y %H:%M', validators=[DataRequired()])

    def validate_timestamp(self, field):
        """
        checks the timestamp is not too far in the past or in the future
        :param field: timestamp
        :type field: datetime
        :return:
        :rtype:
        """
        if self.timestamp.data:
            now = datetime.utcnow()
            delta = now - self.timestamp.data
            if delta.days > 100:  # too far in the past
                raise ValidationError("Please enter a date in the last 100 days")

            if delta.days < -1:  # too far in the future
                raise ValidationError("Please don't enter a future date")
            # adding on 1 millisecond so the ISO string conversion shows milliseconds
            self.timestamp.data += timedelta(milliseconds=1)
