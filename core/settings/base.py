from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()
from datetime import timedelta


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-y*3ugb&7(ay^*1h_u-#s%lsjyvnvg38m10qho6j=-fzo)c*@kd"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "localhost","10.0.2.2", "192.168.1.104", "bc49-117-247-80-58.ngrok-free.app", "0.0.0.0"]


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'corsheaders',
    # "django.contrib.sites",
]

# SITE_ID = 2

EXTERNAL_APPS = [
    'apps.user',
    'apps.role',

    'rest_framework',
    

    # "debug_toolbar",
    # # 'oauth2_provider',
    # # 'apps.auth',
    # 'rest_framework_simplejwt',
    # 'oauth2_provider',
    # "allauth_ui",
    # "allauth",
    # "allauth.account",
    # "allauth.socialaccount",
    # "allauth.socialaccount.providers.google",
    # "widget_tweaks",
]

INSTALLED_APPS += EXTERNAL_APPS


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Added the account middleware:
    "allauth.account.middleware.AccountMiddleware",
    'corsheaders.middleware.CorsMiddleware',
    # "debug_toolbar.middleware.DebugToolbarMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                # `allauth` needs this from django
                'django.template.context_processors.request',
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    "default": {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
        
    }
}

# SECRET_ID = str(os.getenv('WEB_CLIENT_ID'))

# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         'APP': {
#             'client_id': '603432281842-sud928gb4mnhnkjv19276nt9uf1c8ann.apps.googleusercontent.com',
#             'secret': 'AIzaSyD_NFxAA90XeQKPtXTspOXFjUUwFzKC09M',
#             'key': ''
#         },
#         'SCOPE': [
#             'profile',
#             'email',
#         ],
#         'AUTH_PARAMS': {
#             'access_type': 'online', # default
#         },
#         # 'OAUTH_PKCE_ENABLED': True,
#         'EMAIL_AUTHENTICATION': True
#     }
# }


# AUTHENTICATION_BACKENDS = (
#     # Needed to login by username in Django admin, regardless of `allauth`
#     'django.contrib.auth.backends.ModelBackend',
    
#     # `allauth` specific authentication methods, such as login by email
#     'allauth.account.auth_backends.AuthenticationBackend',
# )

# LOGIN_REDIRECT_URL = 'home'

# SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
# ACCOUNT_AUTHENTICATION_METHOD = 'email'
# ACCOUNT_EMAIL_REQUIRED = True
# ACCOUNT_USERNAME_REQUIRED = False
# ACCOUNT_EMAIL_VERIFICATION = 'optional'
# ACCOUNT_ADAPTER = "apps.allauth.accounts.allauth.AccountAdapter"
# EMAIL_BACKEND ='django.core.mail.backends.console.EmailBackend'


# OAUTH2_PROVIDER = {
#     'SCOPES': {'read': 'Read scope', 'write': 'Write scope', 'groups': 'Access to your groups'}
# }

# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         'EMAIL_AUTHENTICATION': False,
#         'APP': {
#             'client_id': os.getenv('GOOGLE_CLIENT_ID'),
#             'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
#         },
#         'SCOPE': [
#             'profile',
#             'email',
#         ],
#         'AUTH_PARAMS': {
#             'access_type': 'online',
#         },
#         'OAUTH_PKCE_ENABLED': True,
#     }
# }

# Provider specific settings
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         # For each OAuth based provider, either add a ``SocialApp``
#         # (``socialaccount`` app) containing the required client
#         # credentials, or list them here:
#         'APP': {
#             'client_id': os.getenv('GOOGLE_CLIENT_ID'),
#             'secret': os.getenv('GOOGLE_CLIENT_SECRET'),
#             'key': ''
#         },
#         'EMAIL_AUTHENTICATION': True,
#         'AUTH_PARAMS': {
#             'access_type': 'offline',
#         },
#         'OAUTH_PKCE_ENABLED': True,
#     }
# }


# INTERNAL_IPS = [
#     # ...
#     "127.0.0.1",
#     # ...
# ]


# TEMPLATE_CONTEXT_PROCESSORS = (
#     "django.core.context_processors.request",
#     "allauth.account.context_processors.account",
#     "allauth.socialaccount.context_processors.socialaccount",
# )


# REST_FRAMEWORK = {
#     'DEFAULT_AUTHENTICATION_CLASSES': (
#         'oauth2_provider.contrib.rest_framework.OAuth2Authentication',
#         'rest_framework_simplejwt.authentication.JWTAuthentication',
        
#     ),

#     'DEFAULT_PERMISSION_CLASSES': (
#         'rest_framework.permissions.IsAuthenticated',
#     ),
# }

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}


SIMPLE_JWT = {
    'AUTH_HEADER_TYPES':('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
}

CORS_ORIGIN_ALLOW_ALL = True
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False
SESSION_COOKIE_SECURE = True

# # Google OAuth2 settings
# GOOGLE_SSO_CLIENT_ID = '235885884053-98m5vbfnv48jq8pqm3airkflco052hff.apps.googleusercontent.com'
# GOOGLE_SSO_CLIENT_SECRET = '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'
# GOOGLE_SSO_ALLOWABLE_DOMAINS = ["gmail.com", "copods.co"]
# GOOGLE_SSO_AUTO_CREATE_USERS = True
# # SSO_SHOW_FORM_ON_ADMIN_PAGE = False
