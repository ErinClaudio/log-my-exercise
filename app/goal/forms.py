from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField, HiddenField
from wtforms.validators import DataRequired, Length, NumberRange, AnyOf, ValidationError, Optional

from app.main import VALID_ACTIVITIES, SELECT_ACTIVITIES


class GoalForm(FlaskForm):
    """
    Represents a user goal
    """
    title = StringField('Goal title *', validators=[DataRequired(), Length(min=1, max=30)])
    motivation = TextAreaField('My motivation for this goal is:', validators=[Length(min=0, max=200)],
                               render_kw={"rows": 3, "cols": 11})
    acceptance_criteria = TextAreaField('I will have met this goal when:', validators=[Length(min=0, max=200)],
                                        render_kw={"rows": 3, "cols": 11})
    reward = TextAreaField('I will reward myself:', validators=[Length(min=0, max=200)],
                           render_kw={"rows": 3, "cols": 11})
    frequency = IntegerField('Frequency', validators=[Optional(), NumberRange(0, 7)], render_kw={"size": 2})
    duration = IntegerField('Duration (mins)',
                            validators=[Optional(),
                                        NumberRange(0, 999, message="Please enter a number between 0 and 999")],
                            render_kw={"size": 3})
    distance = IntegerField('Distance (km)',
                            validators=[Optional(),
                                        NumberRange(0, 999, message="Please enter a number between 0 and 999")],
                            render_kw={"size": 3})
    frequency_activity_type = SelectField('Type', choices=[('-1', 'Any exercise')] + SELECT_ACTIVITIES,
                                          validators=[Optional(),
                                                      AnyOf(['-1'] + VALID_ACTIVITIES)])
    duration_activity_type = SelectField('Type', choices=[('-1', 'Any exercise')] + SELECT_ACTIVITIES,
                                         validators=[Optional(), AnyOf(['-1'] + VALID_ACTIVITIES)])
    distance_activity_type = SelectField('Type', choices=[('-1', 'Any exercise')] + SELECT_ACTIVITIES,
                                         validators=[Optional(),
                                                     AnyOf(['-1'] + VALID_ACTIVITIES)])
    valid_goal = HiddenField('Valid Goal')
    submit = SubmitField('Set Goal')

    def validate_valid_goal(self, field):
        # need to enter at least one value in one of these fields
        if not self.duration.data and not self.distance.data and not self.frequency.data:
            raise ValidationError("Please enter a frequency, duration or distance")
