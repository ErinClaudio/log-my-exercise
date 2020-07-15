from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, URL, NumberRange, AnyOf
from app.main import SELECT_ACTIVITIES, VALID_ACTIVITIES


class InspiresForm(FlaskForm):
    title = StringField('Title *', validators=[DataRequired(), Length(min=0, max=50)])
    url = StringField('Web Link *', validators=[DataRequired(), URL()])
    instructor = StringField('Name of Instructor (optional)', validators=[Length(min=0, max=50)])
    duration = IntegerField('Typical Duration (mins) *',
                            validators=[DataRequired(),
                                        NumberRange(0, 120, message="Please enter a number between 0 and 120")])
    type = SelectField('Type *', choices=SELECT_ACTIVITIES, validators=[AnyOf(VALID_ACTIVITIES)])
    description = TextAreaField('Description *', validators=[DataRequired(), Length(min=0, max=200)])
    why_inspires = TextAreaField('Why does it inspire me *', validators=[DataRequired(), Length(min=0, max=200)])

    submit = SubmitField('Save')
