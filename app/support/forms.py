from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Email


class FeedbackForm(FlaskForm):

    name = StringField('Name *', validators=[DataRequired(), Length(min=0, max=50)])
    email = StringField('Email *', validators=[DataRequired(), Email()])
    description = TextAreaField('Message *', validators=[DataRequired(), Length(min=0, max=500)])
    submit = SubmitField('Say Hello')

