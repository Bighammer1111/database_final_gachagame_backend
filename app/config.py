import datetime
import os

class Config(object):
    # SQLALCHEMY_DATABASE_URI = 'sqlite://///Users/rogerzhang/論文/Project/database/mydatabase.db'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:////data/mydatabase.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///D:/app_backend/APP_Server/flask_server/mydatabase.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = True
    ACCESS_TOKENS = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c'
    SECRET_KEY = 'bfa693af0039c7c858f84f1b42d1edf625003be7bedb2abab1e43086efcff974'
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=14)

