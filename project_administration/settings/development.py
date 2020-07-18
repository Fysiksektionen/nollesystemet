from project_administration.settings.production import *

TMP_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, 'tmp'))

DEBUG = True

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
    '*'
)

CAS_SERVER_URL = 'http://18.156.68.18:3004'

PAGE_CALL_STACK_SIZE = 10

