from flask import jsonify

from . import api
from ..exceptions import ValidationError, RequestBodyEmpty


def bad_request(message: str):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def forbidden(message: str):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


@api.errorhandler(ValidationError)
def validation_error(err: ValidationError):
    return bad_request(err.args[0])


@api.errorhandler(RequestBodyEmpty)
def request_body_empty(err: RequestBodyEmpty):
    return bad_request(err.args[0])
