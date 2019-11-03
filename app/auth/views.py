from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user

from . import auth
from .forms import (LoginForm, RegistrationForm, ChangePasswordForm,
                    PasswordResetRequestForm, PasswordResetForm, ChangeFieldsForm)
from .. import db
from ..models import User
from ..email import send_email

current_user: User


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint and request.blueprint != 'auth':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Yor have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        email: str = form.email.data.lower()
        user = User(form.username.data, email, form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email([email], 'Confirm Your account', 'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been send to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed you account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email([current_user.email], 'Confirm Your account', 'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been update.')
            redirect(url_for('main.index'))
        else:
            flash('Invalid old password')
    return render_template('auth/change_password.html', form=form)


@auth.route('/password_reset_request', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        redirect(url_for('main.index'))

    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        email: str = form.email.data.lower()
        user = User.query.filter_by(email=email).first()
        if user:
            token = user.generate_reset_token()
            send_email([email], 'Reset your password', 'auth/email/reset_password', user=user, token=token)
            flash('A email with instructions has been send to you.')
            return redirect(url_for('.login'))

    return render_template('auth/reset_password.html', form=form)


@auth.route('/password_reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            flash('Your password has been update .')
            return redirect(url_for('.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
def change_email_request():
    form = ChangeFieldsForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data.lower()
            token = current_user.generate_email_change_token(new_email)
            send_email([new_email], 'Confirm yor email address', 'auth/email/change_email',
                       user=current_user, token=token)
            flash('An email with instructions to confirm your email has been sent to you')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid email or password')
    return render_template('auth/change_email.html', form=form)


@auth.route('/change_email/<token>')
def change_email(token):
    if current_user.change_email(token):
        db.session.commit()
        flash('Your email address has been update')
    else:
        flash('Invalid request. Try retrying your email change requests')
    return redirect(url_for('main.index'))
