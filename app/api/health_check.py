from flask import request, jsonify, current_app as app, send_file
import requests
from . import api_hc

@api_hc.route('/', methods=['GET'])
def health_check():
    return 'instai app backend'