from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

from app.blog_form import BlogFields


class PhotoForm(FlaskForm):
    target_image = FileField('Target Image', validators=[FileRequired()])
    style_reference_image = FileField('Style Reference Image', validators=[FileRequired()])
    submit = BlogFields.submit


