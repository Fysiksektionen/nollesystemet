import os
import json

from django.urls import reverse_lazy
from django.utils.log import DEFAULT_LOGGING

def join_urls(*args):
    for arg in args:
        if not isinstance(arg, str):
            raise TypeError("Argument %s is not a string" % str(arg))

    if len(args) > 0:
        path = '/'.join([arg.strip('/') for arg in args])
        if len(args[0]) > 0 and args[0][0] == '/' and path[0] != '/':
            path = '/' + path

        if len(args) > 1:
            if len(args[-1]) > 0 and args[-1][-1] == '/' and path[-1] != '/':
                path = path + '/'
        else:
            if len(args[-1]) > 1 and args[-1][-1] == '/' and path[-1] != '/':
                path = path + '/'
    return path

PROJECT_APP_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
PROJECT_ROOT = PROJECT_APP_ROOT
PUBLIC_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, 'public'))

with open('/etc/django/secret_key.cnf') as f:
    SECRET_KEY = f.read().strip()

with open(os.path.join(os.path.dirname(__file__), 'config_files/settings.json')) as f:
    data = json.load(f)
    ROOT_URL = data['ROOT_URL']

DEBUG = False

ALLOWED_HOSTS = (
    '18.156.68.18',
    'leoenge.se',
)

ADMINS = [('admin', 'ejemyr@fysiksektionen.se')]
MANAGERS = ADMINS

# Application definition

ROOT_URLCONF = 'project_administration.urls'
WSGI_APPLICATION = 'project_administration.wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'multiselectfield',
    'authentication',
    'nollesystemet',
)

MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'nollesystemet.middleware.PageCallStackMiddleware',
)

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(PROJECT_ROOT, 'venv/lib/python3.8/site-packages/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'nollesystemet_db',
        'USER': 'ejemyr',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}

# Internationalization
LANGUAGE_CODE = 'sv'
TIME_ZONE = 'Europe/Stockholm'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    os.path.join(PROJECT_ROOT, 'locale'),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = join_urls(ROOT_URL, '/static/')
STATIC_ROOT = os.path.join(PUBLIC_ROOT, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),

]

MEDIA_URL = join_urls(ROOT_URL, '/media/')
MEDIA_ROOT = os.path.join(PUBLIC_ROOT, 'mediafiles')
MEDIAFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'media'),
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Crispy settings
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Authentication settings
AUTH_USER_MODEL = 'authentication.AuthUser'
USER_PROFILE_MODEL = 'nollesystemet.UserProfile'
USER_PROFILE_SETUP_URL = reverse_lazy('fadderiet:mina-sidor:profil')

AUTHENTICATION_BACKENDS = [
    'authentication.backends.UserCredentialsBackend',
    'authentication.backends.CASBackend',
]

CAS_SERVER_URL = "https://login.kth.se"
LOGIN_URL = reverse_lazy('fadderiet:logga-in:index')

#Email setup
def get_email_info(filename):
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        content = f.read().splitlines()
    options = {}
    for line in content:
        try:
            key, value = line.split('=')
        except:
            raise Exception('Error in file formatting. %s' % filename)
        options[key.strip()] = value.lstrip().strip()
    return options['host'], options['use_tls'] == 'True', int(options['port']), options['username'], options['password']


SERVER_EMAIL = 'cejemyr@gmail.com'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST, EMAIL_USE_TLS, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD = get_email_info('config_files/mail.cnf')


# Assure that errors end up to Apache error logs via console output
# when debug mode is disabled
DEFAULT_LOGGING['handlers']['console']['filters'] = []
# Enable logging to console from our modules by configuring the root logger
DEFAULT_LOGGING['loggers'][''] = {
    'handlers': ['console'],
    'level': 'INFO',
    'propagate': True
}

# PAGE_CALL_STACK_SIZE = 5
