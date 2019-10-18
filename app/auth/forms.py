from flask_wtf import FlaskForm
from wtforms import SubmitField, PasswordField, BooleanField
from wtforms.validators import DataRequired, EqualTo

from ..blog_form import BlogFields, FieldsValidator


class LoginForm(FlaskForm):
    email = BlogFields.email
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')


class RegistrationForm(FlaskForm, FieldsValidator):

    email = BlogFields.email
    username = BlogFields.username
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[DataRequired()])
    submit = SubmitField('Register')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    password = PasswordField('New password', validators=[DataRequired(),
                                                         EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update password')


class PasswordResetRequestForm(FlaskForm):
    email = BlogFields.email
    submit = SubmitField('Reset password')


class PasswordResetForm(FlaskForm):
    password = PasswordField('New password', validators=[DataRequired(),
                                                         EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[DataRequired()])
    submit = SubmitField('Update password')


class ChangeFieldsForm(FieldsValidator, FlaskForm):
    email = BlogFields.email
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Update Email Address')


