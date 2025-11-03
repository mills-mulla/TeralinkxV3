"""
Django settings for teralinkx project.
"""
import dj_database_url
from pathlib import Path
import os
import sys
from dotenv import load_dotenv
from django.conf import settings
from rest_framework.request import Request
from corsheaders.defaults import default_headers

# Load environment variables
load_dotenv()

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Apps directory to Python path
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

#Development settings
DEBUG = True #os.environ.get('DJANGO_DEBUG', 'False') == 'True'

# Security
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-dev-only')

ALLOWED_HOSTS = [
    'login.teralinkxwaves.uk',
    'service.teralinkxwaves.uk',
    'teralinkxwaves.uk',
    'teralinkxwaves.co.ke',
    'teralinkxwaves.spot',
    '192.168.88.108',
    '192.168.88.15',
    '192.168.88.16',
    'localhost',
    '127.0.0.1',
    '192.168.8.8',
    '10.0.0.1',
    
]
# ALLOWED_HOSTS = ['*']
# ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1,192.168.88.108,192.168.88.15').split(',')

# Apps
INSTALLED_APPS = [
    'django_prometheus',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-party
    'channels',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'silk',
    'whitenoise.runserver_nostatic',
    'django_celery_beat',
    
    # Local
    # 'core',
    'users',
    'locations',
    'packages',
    'analytics',
    'finance',
    'security',
    'notifications',
    'sync',
    'ads',
    
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'silk.middleware.SilkyMiddleware',
]

# Security settings
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True #False #True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000 # disables HSTS
    SECURE_HSTS_PRELOAD = True
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    
# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False


# URLs & Templates
ROOT_URLCONF = 'teralinkx.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Databasedocker
# DATABASES = {
#     'default': dj_database_url.config(
#         default='postgres://teralinkx:justboot@db:5432/teralinkx',
#         conn_max_age=600,  # persistent connections
#         ssl_require=False  # set True in production if needed
#     )
# }
#default database sqlite3
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',  # Database engine
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),  # Path to the database file
    }
}

# # localdatabase
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME', ''),
#         'USER': os.environ.get('DB_USER', ''),
#         'PASSWORD': os.environ.get('DB_PASSWORD', ''),
#         'HOST': os.environ.get('DB_HOST', 'localhost'),
#         'PORT': os.environ.get('DB_PORT', '5432'),
#         'OPTIONS': {
#             'connect_timeout': 5,
#         },
#     }
# }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 9}
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
####
# JWT Configuration
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
}
# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# CORS settings
CSRF_COOKIE_SAMESITE = 'None'
CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-csrftoken",
    "authorization",
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    'https://teralinkxwaves.uk',
    'https://login.teralinkxwaves.uk',
    'https://service.teralinkxwaves.uk',
    'http://teralinkxwaves.spot',
    'http://teralinkxwaves.co.ke',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://192.168.8.8:5173',
    'http://192.168.88.16',
    'http://10.0.0.1'
    
]
CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
]
CSRF_TRUSTED_ORIGINS = [
    'https://teralinkxwaves.uk',
    'https://login.teralinkxwaves.uk',
    'https://service.teralinkxwaves.uk',
    'http://teralinkxwaves.spot',
    'http://teralinkxwaves.co.ke',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://192.168.8.8:5173',
    'http://192.168.88.16',
    'http://10.0.0.1'
    
]

# Cache
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
        }
    }
}

# Celery
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://redis:6379/')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://redis:6379/')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend' if not DEBUG else 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'webmaster@localhost')
#pusher
PUSHER_APP_ID =  os.environ.get('PUSHERID', '')
PUSHER_KEY = os.environ.get('PUSHERKEY', '')
PUSHER_SECRET = os.environ.get('PUSHERSCRT', '')
PUSHER_CLUSTER = os.environ.get('PUSHERCLT', '')
PUSHER_SSL = True


# Silk
SILKY_PYTHON_PROFILER = True
SILKY_INTERCEPT_FUNC = lambda request: DEBUG  # Only profile in debug mode

# Channels
ASGI_APPLICATION = 'teralinkx.asgi.application'

