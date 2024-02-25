import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY') or 'set-this-to-the-api-key-from-google'
    SITE_NAME  = os.environ.get('SITE_NAME') or 'Sumpan Lunch'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEFAULT_LOCATION = "Sundbyberg Sweden"
    ADMINS = ['your-email@example.com']
    POSTS_PER_PAGE = 25
    LANGUAGES = ['en', 'es']
    ROCKET_ENABLED = os.environ.get('ROCKET_ENABLED') or False
    ROCKET_USER = os.environ.get('ROCKET_USER') or 'mylunch'
    ROCKET_PASS = os.environ.get('ROCKET_PASS') or 'foo123'
    ROCKET_URL = os.environ.get('ROCKET_URL') or 'http://172.17.0.4:3000'
    ROCKET_CHANNEL = os.environ.get('ROCKET_CHANNEL') or 'GENERAL'
    NON_WORKING_DAYS_COLOR = os.environ.get(
        'NON_WORKING_DAYS_COLOR') or "#FF2222"
    ABSENCE_COLOR = os.environ.get('ABSENCE_COLOR') or "#AAAAAA"
    OPEN_REGISTRATION = os.environ.get('OPEN_REGISTRATION') or True
    ENFORCE_ROLES = os.environ.get('ENFORCE_ROLES') or True
    mylunch_TZ = os.environ.get('mylunch_TZ') or "Europe/Stockholm"

# local means dont use CDN
    BOOTSTRAP_SERVE_LOCAL = os.environ.get('BOOTSTRAP_SERVE_LOCAL') or True
