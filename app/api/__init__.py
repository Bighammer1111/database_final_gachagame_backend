from flask import Blueprint

api_bp = Blueprint('api', __name__)
api_hc = Blueprint('api_health_check', __name__)

from . import routes 
from . import health_check