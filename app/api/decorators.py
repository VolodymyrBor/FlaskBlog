from functools import wraps

from flask import g

from .errors import forbidden


def permission_required(permission):
    def decorator(function):
        @wraps(function)
        def decorator_function(*args, **kwargs):
            if not g.current_user.can(permission):
                forbidden('Insufficient permissions')
            return function(*args, **kwargs)
        return decorator_function
    return decorator
