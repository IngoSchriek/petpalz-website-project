from flask import current_app
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Email, EqualTo, Length, ValidationError


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Log in')

def email_unique(form, field):
    if current_app.db.user.find_one({"email": field.data}):
        raise ValidationError("This email already exists.")
            

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email(), email_unique])
    password = PasswordField(
        "Password",
        validators=[
            InputRequired(),
            Length(
                min=6,
                message="Your password must be at least 6 characters long.",
            ),
        ],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[
            InputRequired(),
            EqualTo(
                "password",
                message="This password did not match the one in the password field.",
            ),
        ],
    )

    submit = SubmitField("Register")
