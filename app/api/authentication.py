from flask import g
from flask_httpauth import HTTPBasicAuth

from app.api import api
from app.models import AnonymousUser, User
from .errors import unauthorized, forbidden

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email, password) -> bool:
    if email == '':
        g.current_user = AnonymousUser()
        return True
    user = User.query.filter_by(email=email).first()
    if user:
        g.current_user = user
        return user.verify_password(password)
    else:
        return False


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    current_user: User = g.current_user
    if not current_user.is_anonymous and not current_user.confirmed:
        return forbidden('Unconfirmed account')
