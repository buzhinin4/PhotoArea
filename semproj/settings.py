from datetime import timedelta
from pathlib import Path
import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = env.str('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
ALLOWED_HOSTS = env.str('ALLOWED_HOSTS', default='').split(' ')

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

# packages
INSTALLED_APPS += [
    'storages',
    'rest_framework',
    'djoser',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'django_filters',
    'corsheaders',
    'django_extensions',
    'phonenumber_field',
]

# apps
INSTALLED_APPS += [
    'apps.users.apps.UsersConfig',
    'apps.photo.apps.PhotoConfig',
    'apps.address.apps.AddressConfig',
    'apps.portfolio.apps.PortfolioConfig',
    'apps.comments.apps.CommentsConfig',
    'apps.news.apps.NewsConfig',
    'apps.order.apps.OrderConfig',
    'apps.schedule.apps.ScheduleConfig',
]

# Custom user model
AUTH_USER_MODEL = 'users.User'

# after apps
INSTALLED_APPS += [
    'drf_spectacular',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
]

ROOT_URLCONF = 'semproj.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
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

WSGI_APPLICATION = 'semproj.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('PG_DATABASE', 'postgres'),
        'USER': env.str('PG_USER', 'postgres'),
        'PASSWORD': env.str('PG_PASSWORD', 'postgres'),
        'HOST': env.str('DB_HOST', 'localhost'),
        'PORT': env.int('DB_PORT', 5432),
    },
    'extra': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    },
}

###########################
# DJANGO REST FRAMEWORK
###########################
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',),

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],

    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FileUploadParser',
    ],
    # 'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    # 'DEFAULT_PAGINATION_CLASS': 'common.pagination.BasePagination',
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/'
# STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
# DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    },
}


MEDIA_URL = f"{env.str('AWS_S3_ENDPOINT_URL')}/{env.str('MINIO_BUCKET_NAME')}/"
MINIO_BUCKET_NAME = env.str('MINIO_BUCKET_NAME')  # 'photos'
MINIO_ENDPOINT = env.str('MINIO_STORAGE_ENDPOINT')  # 'localhost:9000'
MINIO_ACCESS_KEY = env.str('MINIO_STORAGE_ACCESS_KEY')  # 'minioadmin1'
MINIO_SECRET_KEY = env.str('MINIO_STORAGE_SECRET_KEY')  # 'minioadmin1'
AWS_ACCESS_KEY_ID = MINIO_ACCESS_KEY
AWS_SECRET_ACCESS_KEY = MINIO_SECRET_KEY
AWS_STORAGE_BUCKET_NAME = MINIO_BUCKET_NAME
AWS_S3_ENDPOINT_URL = f"http://{MINIO_ENDPOINT}"
AWS_S3_USE_SSL = False
AWS_S3_VERIFY = False
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_DEFAULT_ACL = None
AWS_QUERYSTRING_AUTH = True
AWS_S3_FILE_OVERWRITE = False

# MINIO_STORAGE_ENDPOINT = env.str('MINIO_STORAGE_ENDPOINT')  # 'localhost:9000'
# MINIO_STORAGE_ACCESS_KEY = env.str('MINIO_STORAGE_ACCESS_KEY')  # 'minioadmin'
# MINIO_STORAGE_SECRET_KEY = env.str('MINIO_STORAGE_SECRET_KEY')  # 'minioadmin'
# MINIO_STORAGE_USE_HTTPS = env.bool('MINIO_STORAGE_USE_HTTPS', default=False)
# MINIO_STORAGE_MEDIA_BUCKET_NAME = env.str('MINIO_STORAGE_MEDIA_BUCKET_NAME')  # 'media'
# MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET = env.bool('MINIO_STORAGE_AUTO_CREATE_MEDIA_BUCKET', default=True)
# MINIO_STORAGE_STATIC_BUCKET_NAME = env.str('MINIO_STORAGE_STATIC_BUCKET_NAME')  # 'static'
# MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET = env.bool('MINIO_STORAGE_AUTO_CREATE_STATIC_BUCKET', default=True)
# MINIO_STORAGE_MEDIA_URL = env.str('MINIO_STORAGE_MEDIA_URL')  # 'http://localhost:9000/media/'
# MINIO_STORAGE_STATIC_URL = env.str('MINIO_STORAGE_STATIC_URL')  # 'http://localhost:9000/static/'
#
# STATIC_URL = '/static/'
# STATICFILES_STORAGE = 'django_minio_storage.storage.MinioStaticStorage'
#
# DEFAULT_FILE_STORAGE = 'django_minio_storage.storage.MinioMediaStorage'
# MEDIA_URL = env.str('MINIO_STORAGE_MEDIA_URL')

# STATIC_URL = 'static/'
#
# MEDIA_ROOT = BASE_DIR / 'media'
# MEDIA_URL = '/media/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

######################
# CORS HEADERS
######################
CORS_ALLOW_ALL_ORIGINS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ['*']
CSRF_COOKIE_SECURE = False

#######################
# DJOSER
#######################
DJOSER = {
    'PASSWORD_RESET_CONFIRM_URL': '#/password/reset/confirm/{uid}/{token}',
    'USERNAME_RESET_CONFIRM_URL': '#/username/reset/confirm/{uid}/{token}',
    'ACTIVATION_URL': '#/activate/{uid}/{token}',
    'SEND_ACTIVATION_EMAIL': False,
    'SERIALIZERS': {
        # 'user_create': 'apps.users.serializers.CustomUserCreateSerializer',
        # 'user': 'apps.users.serializers.CustomUserSerializer',
        # 'current_user': 'apps.users.serializers.CustomUserSerializer',
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(hours=24),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=1),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
}

######################
# DRF SPECTACULAR
######################
SPECTACULAR_SETTINGS = {
    'TITLE': 'Kitchen Helper',
    'DESCRIPTION': 'Kitchen Helper',
    'VERSION': '1.0.0',

    'SERVE_PERMISSIONS': [
        'rest_framework.permissions.AllowAny',
    ],

    'SERVE_AUTHENTICATION': [
        'rest_framework.authentication.BasicAuthentication',
    ],

    'SWAGGER_UI_SETTINGS': {
        'deepLinking': True,
        "displayOperationId": True,
        # "syntaxHighlight.active": True,
        # "syntaxHighlight.theme": "arta",
        # "defaultModelsExpandDepth": -1,
        # "displayRequestDuration": True,
        # "filter": True,
        # "requestSnippetsEnabled": True,
    },

    'COMPONENT_SPLIT_REQUEST': True,
    'SORT_OPERATIONS': False,

    'ENABLE_DJANGO_DEPLOY_CHECK': False,
    'DISABLE_ERRORS_AND_WARNINGS': True,
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'storages': {
            'handlers': ['console'],
            'level': 'DEBUG',
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
#
# print("MEDIA_URL:", env.str('MINIO_STORAGE_MEDIA_URL'))
# print("DEFAULT_FILE_STORAGE:", DEFAULT_FILE_STORAGE)

