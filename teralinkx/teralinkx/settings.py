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

# Development settings
DEBUG = True  # Force debug mode for development

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
    '0.0.0.0',  # Added for Docker compatibility
]

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
    'core',
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
    'django.middleware.csrf.CsrfViewMiddleware',  # Keep this enabled
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'silk.middleware.SilkyMiddleware',
]

# ========== DEVELOPMENT SECURITY SETTINGS ==========
# Override all production security settings for development
SECURE_PROXY_SSL_HEADER = None
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False  # Allow HTTP in development
CSRF_COOKIE_SECURE = False     # Allow HTTP in development
SECURE_HSTS_SECONDS = 0        # Disable HSTS in development
SECURE_HSTS_PRELOAD = False
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_CONTENT_TYPE_NOSNIFF = True  # Keep this for security
SECURE_BROWSER_XSS_FILTER = True    # Keep this for security
X_FRAME_OPTIONS = 'DENY'            # Keep this for security

# Session settings for development
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_COOKIE_SECURE = False  # HTTP in development
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'  # Change from 'None' to 'Lax' for development
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# CSRF settings for development
CSRF_COOKIE_SECURE = False      # HTTP in development
CSRF_COOKIE_HTTPONLY = False    # Allow JavaScript access if needed
CSRF_COOKIE_SAMESITE = 'Lax'    # Change from 'None' to 'Lax'
CSRF_USE_SESSIONS = False       # Use cookies instead of sessions
CSRF_FAILURE_VIEW = 'django.views.csrf.csrf_failure'

# URLs & Templates
ROOT_URLCONF = 'teralinkx.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Database - SQLite for development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

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
        'rest_framework.permissions.AllowAny', 
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',  # Enable browsable API in development
    )
}

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

# ========== CORS SETTINGS FOR DEVELOPMENT ==========
CORS_ALLOW_HEADERS = list(default_headers) + [
    "x-csrftoken",
    "authorization",
    "content-type",
]

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    'http://teralinkxwaves.uk',
    'http://login.teralinkxwaves.uk',
    'http://service.teralinkxwaves.uk',
    'http://teralinkxwaves.spot',
    'http://teralinkxwaves.co.ke',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://192.168.88.16:8200',
    'http://192.168.8.8:5173',
    'http://192.168.88.16',
    'http://10.0.0.1',
    'http://0.0.0.0:8000',
]

# For development, you can also allow all origins (be careful in production)
CORS_ALLOW_ALL_ORIGINS = True  # Enable this for development only

CORS_ALLOW_METHODS = [
    'DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT',
]

CSRF_TRUSTED_ORIGINS = [
    'http://teralinkxwaves.uk',
    'http://login.teralinkxwaves.uk',
    'http://service.teralinkxwaves.uk',
    'http://teralinkxwaves.spot',
    'http://teralinkxwaves.co.ke',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://192.168.8.8:5173',
    'http://192.168.88.16:8200',
    'http://192.168.88.16',
    'http://10.0.0.1',
    'http://0.0.0.0:8000',
]

# Cache
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",  # Use local memory cache for development
        "LOCATION": "unique-snowflake",
    }
}

# Alternative Redis cache for development (if you have Redis running)
# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": "redis://127.0.0.1:6379/1",
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#         }
#     }
# }

# Celery - development settings
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # Local Redis
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

# Email - console backend for development
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 25
EMAIL_USE_TLS = False
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
DEFAULT_FROM_EMAIL = 'webmaster@localhost'

# Pusher - development settings (optional)
PUSHER_APP_ID = os.environ.get('PUSHERID', '')
PUSHER_KEY = os.environ.get('PUSHERKEY', '')
PUSHER_SECRET = os.environ.get('PUSHERSCRT', '')
PUSHER_CLUSTER = os.environ.get('PUSHERCLT', '')
PUSHER_SSL = False  # Disable SSL for development

# Silk - enable in development
SILKY_PYTHON_PROFILER = True
SILKY_INTERCEPT_FUNC = lambda request: DEBUG

# Channels
ASGI_APPLICATION = 'teralinkx.asgi.application'

# Logging for development
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
} 