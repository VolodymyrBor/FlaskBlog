from flask_wtf import FlaskForm
from wtforms import BooleanField, SelectField, ValidationError, SubmitField, TextAreaField
from wtforms.validators import DataRequired

from ..models import User, Role
from ..blog_form import BlogFields, FieldsValidator


class NameForm(FlaskForm):
    username = BlogFields.username
    submit = BlogFields.submit


class EditProfileForm(FlaskForm):
    name = BlogFields.name
    location = BlogFields.location
    about_me = BlogFields.about_me
    submit = BlogFields.submit


class EditProfileAdminForm(FlaskForm, FieldsValidator):
    email = BlogFields.email
    username = BlogFields.username
    name = BlogFields.name
    location = BlogFields.location
    about_me = BlogFields.about_me
    confirmed = BooleanField('Confirmed')
    role = SelectField('Role', coerce=int)
    submit = SubmitField('Submit')

    def __init__(self, user: User, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name) for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')


class PostForm(FlaskForm):
    body = TextAreaField("What's on your mind?", validators=[DataRequired()])
    submit = SubmitField('Submit')
