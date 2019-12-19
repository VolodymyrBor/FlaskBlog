from shutil import copyfile
from typing import List
from uuid import uuid4

from flask import render_template, flash, current_app, Flask, redirect, url_for
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from style_transfer import StyleTransfer
from app.models import Images, User
from app.images_path import ImagesPath
from . import transfer
from .forms import PhotoForm
from app import db

current_user: User
current_app: Flask


@transfer.route('/style_transfer', methods=['GET', 'POST'])
@login_required
def style_transfer():
    form = PhotoForm()

    if form.validate_on_submit():
        username = current_user.username
        image_path = ImagesPath(username, current_app.static_folder)

        target_image = form.target_image.data
        style_reference_image = form.style_reference_image.data

        target_image_name = secure_filename(target_image.filename)
        style_reference_image_name = secure_filename(style_reference_image.filename)

        target_image_path = image_path.buffer_image_path(target_image_name)
        style_reference_image_path = image_path.buffer_image_path(style_reference_image_name)

        target_image_path_abs = image_path.abs_path(target_image_path)
        style_reference_image_path_abs = image_path.abs_path(style_reference_image_path)

        target_image.save(target_image_path_abs)
        style_reference_image.save(style_reference_image_path_abs)

        flash('Wait for result image.')

        StyleTransfer(target_image_path_abs,
                      style_reference_image_path_abs,
                      save_path=image_path.model_buffer(absolute=True),
                      iterations=current_app.config['MODEL_ITERATION']).transfer()

        result_image_path = image_path.last_file_path()

        return render_template('transfer/image_transfer.html',
                               target_image_path=image_path.convert(target_image_path),
                               style_reference_image_path=image_path.convert(style_reference_image_path),
                               form=form,
                               result_image_path=image_path.convert(result_image_path),
                               username=username)
    return render_template('transfer/image_transfer.html', form=form)


@transfer.route('/save_image/<username>')
@login_required
def save_image(username):
    image_path = ImagesPath(username, current_app.static_folder)

    src = image_path.last_file_path(absolute=True)
    filename = f'{uuid4().hex}.jpg'
    dst = image_path.save_image_path(filename, absolute=True)
    copyfile(src, dst)

    user = User.get_user_by_name(username)
    img = Images(filename=filename, author=user)
    db.session.add(img)
    db.session.commit()

    return redirect(url_for('.style_transfer'))


@transfer.route('/gallery/<username>')
def gallery(username):
    img_path = ImagesPath(username, current_app.static_folder)
    images_names = img_path.get_save_images_name()
    images_relative_path = [
        img_path.convert(img_path.save_image_path(filename=images_name))
        for images_name in images_names
    ]
    return render_template('transfer/gallery.html', images_relative_path=images_relative_path)
