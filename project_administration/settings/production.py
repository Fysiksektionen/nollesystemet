import os

from django.urls import reverse_lazy

gettext_noop = lambda s: s

PROJECT_APP_ROOT = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
PROJECT_ROOT = PROJECT_APP_ROOT
PUBLIC_ROOT = os.path.abspath(os.path.join(PROJECT_ROOT, 'public'))

SECRET_KEY = 'xb6-3)%wyspw@2*4rd^$a!@56ixbwq4g+2721(2)ica-r8_1#8'

DEBUG = False
TEMPLATE_DEBUG = False

SITE_ID = 1

ALLOWED_HOSTS = (
    'f.kth.se',
)

ADMINS = (
    ('admin', 'ejemyr@kth.se'),
)
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
        'OPTIONS': {
            'read_default_file': os.path.join(os.path.dirname(__file__), 'config_files/db_info.cnf')
        }
    }
}

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Stockholm'
USE_I18N = True
USE_L10N = True
USE_TZ = True

LOCALE_PATHS = [
    os.path.join(PROJECT_ROOT, 'locale'),
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PUBLIC_ROOT, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'static'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PUBLIC_ROOT, 'mediafiles')
MEDIAFILES_DIRS = [
    os.path.join(PROJECT_ROOT, 'media'),
]

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Logging

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'formatters': {
#         'simple': {
#             'format': '%(levelname)s %(message)s'
#         },
#     },
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse',
#         }
#     },
#     'handlers': {
#         'null': {
#             'level': 'DEBUG',
#             'class': 'logging.NullHandler',
#         },
#         'console': {
#             'level': 'DEBUG',
#             'class': 'logging.StreamHandler',
#             'formatter': 'simple'
#         },
#         'mail_admins': {
#             'level': 'ERROR',
#             'class': 'django.utils.log.AdminEmailHandler',
#             'filters': ['require_debug_false'],
#             'include_html': True,
#         }
#     },
#     'loggers': {
#         'django': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': False,
#         },
#         'django.db.backends': {
#             'handlers': ['null'],
#             'level': 'DEBUG',
#         },
#         'py.warnings': {
#             'handlers': ['null'],
#             'level': 'WARNING',
#             'propagate': False,
#         }
#     }
# }


# Crispy settings
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Authentication settings
AUTH_USER_MODEL = 'authentication.AuthUser'
USER_PROFILE_MODEL = 'nollesystemet.UserProfile'
USER_PROFILE_SETUP_URL = reverse_lazy('fadderiet:mina-sidor:profil')

AUTHENTICATION_BACKENDS = [
    'authentication.backends.MultipleGroupCategoriesBackend',
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


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST, EMAIL_USE_TLS, EMAIL_PORT, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD = get_email_info('config_files/mail.cnf')

