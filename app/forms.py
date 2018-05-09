from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import Srep


class LoginForm(FlaskForm):
    repcode = StringField('Rep Code', validators=[DataRequired()])
    teamcode = PasswordField('Team Code', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    repcode = StringField('RepCode', validators=[DataRequired()])
    teamcode = StringField('TeamCode', validators=[DataRequired()])
    submit = SubmitField('Register')

class BeginForm(FlaskForm):
    leaver = SelectField('Leaver', choices=[])
    submit = SubmitField('Select Leaver')

class RefreshForm(FlaskForm):
    refresh = SubmitField('Refresh Possible Matches')

class UpdateForm(FlaskForm):
    tracked = SelectField('Tracked Users', choices=[])
    c4u = SubmitField('Check for Update')

class TestForm(FlaskForm):
    turboscrape = SubmitField('Turbo Scrape')
