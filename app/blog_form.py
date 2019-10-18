import re
from abc import abstractmethod

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Regexp, ValidationError

from .models import User


class BlogFields(FlaskForm):
    _username_regex = re.compile(r'^[A-Za-z][A-Za-z0-9_.]*$')
    _error_messages = [
        'Username must have only letters',
        'numbers',
        'dots',
        'underscores'
    ]

    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username', validators=[DataRequired(),
                                                   Length(1, 64),
                                                   Regexp(_username_regex, 0, _error_messages)])
    name = StringField('Real name', validators=[Length(0, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    about_me = TextAreaField('About me')
    submit = SubmitField('Submit')


class FieldsValidator:

    @abstractmethod
    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already registered.')

    @abstractmethod
    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')