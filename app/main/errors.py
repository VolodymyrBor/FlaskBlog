from flask import render_template, request, jsonify
from . import main


@main.app_errorhandler(404)
def page_not_found(err):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(err):
    return render_template('500.html'), 500


@main.app_errorhandler(403)
def forbidden(err):
    return render_template('403.html'), 403
