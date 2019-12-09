from flask import Blueprint

transfer = Blueprint('transfer', __name__)

from . import view
