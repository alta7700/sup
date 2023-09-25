from pathlib import Path
from dotenv import dotenv_values


BASE_DIR = Path(__file__).resolve().parent.parent

env = dotenv_values(BASE_DIR / '.env')
DEBUG = env["DEBUG"].lower() in ('true', '1') if "DEBUG" in env else True  # 1 or 0


INSTALLED_APPS = [
    'vk_bot.apps.VkBotConfig',
    'reports.apps.ReportsConfig',
    'usersext.apps.UsersextConfig',
    'tables.apps.TablesConfig',

    'django_json_widget',

    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ReportsDjango.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'custom_tags': 'tables.custom_tags'
            }
        },
    },
]

WSGI_APPLICATION = 'ReportsDjango.wsgi.application'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'ru-RU'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

STATIC_ROOT = BASE_DIR / 'static'

STATIC_URL = '/static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/admin_panel/login/'


def list_from_env_value(name: str, required=False):
    value = env.get(name, '')
    assert value if required else True, f'{name} must be in env'
    return [item for item in value.split(',') if item]


SECRET_KEY = env['SECRET_KEY']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env['DB_NAME'],
        'USER': env['DB_USER'],
        'PASSWORD': env['DB_PASSWORD'],
        'HOST': env['DB_HOST'],
        'PORT': env['DB_PORT'],
    }
}

VK_API_VERSION = env['VK_API_VERSION']
VK_USER_TK = env['VK_USER_TK']
VK_GROUP_TK = env['VK_GROUP_TK']
VK_INT_GROUP_ID = int(env['VK_GROUP_ID'])
VK_STR_GROUP_ID = f'-{VK_INT_GROUP_ID}'
VK_CALLBACK_SECRET_KEY = env['VK_CALLBACK_SECRET_KEY']
VK_CALLBACK_CONFIRMATION_CODE = env['VK_CALLBACK_CONFIRMATION_CODE']
VK_APP_ID = int(env['VK_APP_ID'])
VK_GROUP_OWNER_ID = int(env['VK_GROUP_OWNER_ID'])
CURRENT_HALF = int(env.get('CURRENT_HALF', 1))

ALLOWED_HOSTS = list_from_env_value('ALLOWED_HOSTS')
CSRF_TRUSTED_ORIGINS = list_from_env_value('CSRF_TRUSTED_ORIGINS')
YADISK_TOKEN = env['YADISK_TOKEN']

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CHANGE_REPORT_DAYS = int(env.get('CHANGE_REPORT_DAYS', 365))

del env
