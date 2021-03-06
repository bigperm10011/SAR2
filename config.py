import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'fiftenn-fifty-three'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app1.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = 1
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or 'jdbuhrman'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'Jberm100*'
    ADMINS = ['jdbuhrman@gmail.com']
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
