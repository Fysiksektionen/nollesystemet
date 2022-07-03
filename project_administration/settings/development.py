from project_administration.settings.production import *

TMP_PATH = os.path.abspath(os.path.join(PROJECT_ROOT, 'tmp'))

DEBUG = True
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

if 'debug_toolbar' not in INSTALLED_APPS:
    INSTALLED_APPS += ('debug_toolbar',)

ALLOWED_HOSTS = (
    '*'
)

