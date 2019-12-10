from flask import render_template, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.models import User
from app.images_path import ImagesPath
from . import transfer
from .forms import PhotoForm

current_user: User


@transfer.route('/style_transfer', methods=['GET', 'POST'])
@login_required
def style_transfer():
    form = PhotoForm()

    if form.validate_on_submit():
        image_path = ImagesPath(current_user.username)

        target_image = form.target_image.data
        style_reference_image = form.style_reference_image.data

        target_image_name = secure_filename(target_image.filename)
        style_reference_image_name = secure_filename(style_reference_image.filename)

        target_image_path = image_path.buffer_image_path(target_image_name)
        style_reference_path = image_path.buffer_image_path(style_reference_image_name)

        target_image.save(target_image_path)
        style_reference_image.save(style_reference_path)

        flash('Wait for result image.')

        return render_template('transfer/image_transfer.html',
                               target_image_path=target_image_path,
                               style_reference_path=style_reference_path,
                               form=form)
    return render_template('transfer/image_transfer.html', form=form)
