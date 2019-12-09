import os

from flask import Flask, render_template
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename

from app.blog_form import BlogFields
from . import uploads

current_app: Flask


class PhotoForm(FlaskForm):
    photo = FileField(validators=[FileRequired()])
    submit = BlogFields.submit


@uploads.route('/upload', methods=['POST', 'GET'])
def upload():
    form = PhotoForm()
    if form.validate_on_submit():
        f = form.photo.data
        filename = secure_filename(f.filename)
        filepath = os.path.join('images', filename)
        f.save(filepath)
        return render_template('upload/upload.html', filename=filename)
    return render_template('upload/upload.html', form=form)
