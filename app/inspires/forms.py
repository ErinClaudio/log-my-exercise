from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, URL, NumberRange


class InspiresForm(FlaskForm):
    name = StringField('Name *', validators=[DataRequired(), Length(min=0, max=50)])
    title = StringField('Title *', validators=[DataRequired(), Length(min=0, max=50)])
    url = StringField('Web Link *', validators=[DataRequired(), URL()])
    instructor = StringField('Title *', validators=[DataRequired(), Length(min=0, max=50)])
    duration = IntegerField('Duration (mins) *',
                            validators=[DataRequired(),
                                        NumberRange(0, 999, message="Please enter a number between 0 and 999")])
    type = SelectField('Exercise Type *',
                       choices=[('Workout', '0'), ('Yoga', '1')], validators=[DataRequired()])
    description = TextAreaField('Description *', validators=[DataRequired(), Length(min=0, max=200)])
    why_inspires = TextAreaField('Why does it inspire *', validators=[DataRequired(), Length(min=0, max=200)])

    submit = SubmitField('Say Hello')
