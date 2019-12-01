from flask import g, jsonify, current_app, Flask
from flask_httpauth import HTTPBasicAuth

from app.api import api
from app.models import AnonymousUser, User
from .errors import unauthorized, forbidden

current_app: Flask

auth = HTTPBasicAuth()


@api.before_request
@auth.login_required
def before_request():
    current_user: User = g.current_user
    if not current_user.is_anonymous and not current_user.confirmed:
        return forbidden('Unconfirmed account')


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@auth.verify_password
def verify_password(email_or_token: str, password: str) -> bool:
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None

    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False

    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@api.route('/token')
def get_token():
    current_user: User = g.current_user
    if current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    expiration = current_app.config['TTL_TOKEN']
    return jsonify({
        'token': current_user.generate_auth_token(expiration=expiration),
        'expiration': expiration
    })



