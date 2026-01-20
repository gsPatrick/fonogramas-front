from flask import Blueprint

usuario_bp = Blueprint('usuario', __name__, url_prefix='/app', template_folder='templates')

from . import routes
