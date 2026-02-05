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
DEBUG = False  # Production ready

# Security
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-dev-only')

ALLOWED_HOSTS = [
    'test.teralinkxwaves.uk',
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
    '0.0.0.0',
]

# Apps
INSTALLED_APPS = [
    'django_prometheus',
    'django_json_widget',
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
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
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

# Middleware - JWT-only, CSRF disabled
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',  # Disabled for JWT-only API
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.last_seen_middleware.LastSeenMiddleware',
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

# Database - PostgreSQL for production
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL', 'postgresql://teralinkx:justboot@db:5432/teralinkxv3')
    )
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

# REST Framework - JWT-only authentication
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
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
STATIC_URL = '/v3/static/'
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_URL = '/v3/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


###############################################################
##################### CORS Configuration ######################
# Production CORS settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    'https://teralinkxwaves.uk',
    'https://login.teralinkxwaves.uk',
    'https://service.teralinkxwaves.uk',
    'http://teralinkxwaves.spot',
    'http://teralinkxwaves.co.ke',
    'http://localhost:8009',
    'http://127.0.0.1:8009',
    'http://localhost:5173',
    'http://127.0.0.1:5173',
    'http://192.168.88.16:8009',
    'http://192.168.88.16:5173',
    'http://192.168.88.16',
    'http://10.0.0.1',
    'http://0.0.0.0:8000',
]

# CORS_ALLOWED_ORIGINS = [
#     'https://test.teralinkxwaves.uk',
#     'https://teralinkxwaves.uk',
#     'https://login.teralinkxwaves.uk', 
#     'https://service.teralinkxwaves.uk',
#     'http://localhost:5173',  # Dev frontend
#     'http://127.0.0.1:5173',
#     'http://192.168.88.16:5173', #V3 frontend

# ]

CORS_ALLOW_CREDENTIALS = True


# Expose  headers to frontend
CORS_EXPOSE_HEADERS = [
    'Content-Range',
    'X-Content-Range',
    'X-Session-ID',
    'X-Client-Version',
]
CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-csrftoken',
    'authorization',
    'content-type',
    'x-client-timestamp',  
    'x-session-id',       
    'x-client-version',   
    'x-hotspot-name',     
]



# Allowed methods
CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
CSRF_TRUSTED_ORIGINS = [
    'https://test.teralinkxwaves.uk',
    'https://teralinkxwaves.uk',
    'https://login.teralinkxwaves.uk',
    'https://service.teralinkxwaves.uk',
    'http://192.168.88.16:8009',  # V3 port
    'http://127.0.0.1:8009',
]

# Cache - Redis for production
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Celery Configuration - Docker optimized
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

# Task timeout and cleanup settings
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes soft limit
CELERY_TASK_TIME_LIMIT = 600       # 10 minutes hard limit
CELERY_TASK_ACKS_LATE = True       # Acknowledge after task completion
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Process one task at a time

# Result backend cleanup
CELERY_RESULT_EXPIRES = 3600        # Results expire after 1 hour
CELERY_TASK_RESULT_EXPIRES = 3600   # Task results expire after 1 hour
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
CELERY_RESULT_BACKEND_MAX_RETRIES = 10

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

# Silk - disable profiler to avoid conflicts
SILKY_PYTHON_PROFILER = False
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