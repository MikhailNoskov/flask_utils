from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[
        InputRequired(),
        EqualTo('confirm', message='Password must match')
    ])
    confirm = PasswordField('Confirm Password',[InputRequired()])


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])


class AdminUserCreateForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    admin = BooleanField('Is Admin?')


class AdminUserUpdateForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    admin = BooleanField('Is Admin?')
