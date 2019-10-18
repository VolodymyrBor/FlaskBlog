from functools import wraps

from flask import abort
from flask_login import current_user

from app.models import User, Permission

current_user: User


def permission_required(permission):
    def decorator(function):
        @wraps(function)
        def decorator_function(*args, **kwargs):
            if not current_user.can(permission):
                abort(403)
            return function(*args, **kwargs)
        return decorator_function
    return decorator


def admin_required(function):
    return permission_required(Permission.ADMIN)(function)


