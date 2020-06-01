from project_administration.settings.production import *

TMP_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, 'tmp'))

DEBUG = TEMPLATE_DEBUG = True
SECRET = '42'

if 'debug_toolbar' not in INSTALLED_APPS:
    INSTALLED_APPS += ('debug_toolbar',)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': os.path.join(os.path.dirname(__file__), 'config_files/db_info_debug.cnf')
        }
    }
}

ALLOWED_HOSTS = (
    '127.0.0.1',
    'localhost',
    '192.168.0.1',
)

CAS_SERVER_URL = "http://localhost:3004"
