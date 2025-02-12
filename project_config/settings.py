"""
Django settings for project_config project.

Generated by 'django-admin startproject' using Django 4.1.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from pathlib import Path

from environs import Env
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

env = Env()
env.read_env()

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-#8k8zuqd_h*(4f&egh_!y13*3*brb8)oxizp)*$d5g2a2+m28-'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool('DEBUG', default=True)

ALLOWED_HOSTS = ['*']

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # third party
    'allauth',
    'allauth.account',
    'dj_rest_auth',
    'dj_rest_auth.registration',
    'rest_framework',
    'rest_framework.authtoken',
    "corsheaders",
    "drf_spectacular",
    'drf_spectacular_sidecar',  # required for Django collectstatic discovery
    "drf_link_header_pagination",
    "channels",

    # local
    'users',
    'scripts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project_config.urls'

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
        },
    },
]

WSGI_APPLICATION = 'project_config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

# DATABASES = {
#     # sqlite3 is used for development
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

DATABASES = {
    'default': env.dj_db_url("DATABASE_URL", default="sqlite:///db.sqlite3")
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

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

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.CustomUser'

SITE_ID = 1

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'dj_rest_auth.jwt_auth.JWTCookieAuthentication',
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    'DEFAULT_PAGINATION_CLASS': 'drf_link_header_pagination.LinkHeaderPagination',
    'PAGE_SIZE': 10,
}

AUTHENTICATION_BACKENDS = [
    'allauth.account.auth_backends.AuthenticationBackend',
    'django.contrib.auth.backends.ModelBackend',
]

SPECTACULAR_SETTINGS = {
    "TITLE": "Automation API Docs",
    "DESCRIPTION": "docs for automation api endpoints and models",
    "VERSION": "1.0.0",
    'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

REST_USE_JWT = True

JWT_AUTH_COOKIE = 'jwt-auth'
JWT_AUTH_REFRESH_COOKIE = 'jwt-refresh'

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_AUTHENTICATION_METHOD = 'username_email'

# TOken expiration time settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=15),
    'ROTATE_REFRESH_TOKENS': True,
}

# disable email confirmation for now
ACCOUNT_EMAIL_VERIFICATION = 'none'
# ACCOUNT_CONFIRM_EMAIL_ON_GET = True

LOGIN_URL = 'http://localhost:8000/users/login'

# TODO: check how to handle desktop apps requests
#  there is no one url for a frontend, but every user have their own
CORS_ALLOWED_ORIGINS = ("http://localhost:4200",)
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ["http://localhost:4200"]

STATIC_URL = env.str('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / 'static'

# ASGI CONFIGURATION FOR CHANNELS
ASGI_APPLICATION = 'project_config.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
