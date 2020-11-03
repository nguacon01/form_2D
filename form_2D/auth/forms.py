from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class SignupForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=4, max=25)]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(min=6),
            Email(message="Enter your valid email!")
        ]
    )
    password = PasswordField(
        "Password",
        validators=[
            DataRequired(),
            Length(min=6,message="Password length must be more than 6 characters"),
            EqualTo('confirm', message="Passwords must match")
        ]
    )
    confirm = PasswordField(
        "Confirm password",
        validators=[
            DataRequired()
        ]
    )
    first_name = StringField(
        "First Name",
        validators=[
            Optional()
        ]
    )
    last_name = StringField(
        "Last Name",
        validators=[
            Optional()
        ]
    )
    phone_nb = StringField(
        "Phone Number",
        validators=[
            Optional()
        ]
    )
    address = StringField(
        "Address",
        validators=[
            Optional()
        ]
    )
    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    """User Log-in Form."""
    email = StringField(
        'Email',
        validators=[
            DataRequired(),
            Email(message='Enter a valid email.')
        ]
    )
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class ProfileForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[DataRequired(), Length(min=4, max=25)]
    )

    email = StringField(
        "Email",
        validators=[
            DataRequired(),
            Length(min=6),
            Email(message="Enter your valid email!")
        ]
    )
    old_password = PasswordField(
        "Old Password",
        validators=[
            DataRequired()
        ]
    )
    new_password = PasswordField(
        "New Password",
        validators=[
            DataRequired(),
            Length(min=6,message="Password length must be more than 6 characters"),
            EqualTo('confirm', message="Passwords must matche.") 
        ]
    )
    confirm = PasswordField(
        "Confirm new password",
        validators=[
            DataRequired()
        ]
    )
    first_name = StringField(
        "First Name",
        validators=[
            Optional()
        ]
    )
    last_name = StringField(
        "Last Name",
        validators=[
            Optional()
        ]
    )
    phone_nb = StringField(
        "Phone Number",
        validators=[
            Optional()
        ]
    )
    address = StringField(
        "Address",
        validators=[
            Optional()
        ]
    )
    submit = SubmitField("Register")