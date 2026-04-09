"""
Django settings for teralinkx project.
"""
try:
    import dj_database_url
except ImportError:
    dj_database_url = None

from pathlib import Path
import os
import sys
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from django.conf import settings
try:
    from rest_framework.request import Request
except ImportError:
    pass

try:
    from corsheaders.defaults import default_headers
except ImportError:
    default_headers = []

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Apps directory to Python path
sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))

# Development settings
DEBUG = False  # Production ready

# Security - Persistent JWT Secret Management
from .jwt_manager import jwt_manager

# Get or create persistent JWT secret
jwt_secret, jwt_version, is_new_secret = jwt_manager.get_or_create_secret()

# Use persistent secret for JWT
SECRET_KEY = jwt_secret
JWT_SECRET_VERSION = jwt_version

ALLOWED_HOSTS = [
    # Production subdomains
    'teralinkxwaves.uk',
    '*.teralinkxwaves.uk',
    'cli.teralinkxwaves.uk',
    'srv.teralinkxwaves.uk',
    'su.teralinkxwaves.uk',
    'service.teralinkxwaves.uk',
    'account.teralinkxwaves.uk',
    'accounts.teralinkxwaves.uk',
    'adm.teralinkxwaves.uk',
    'router.teralinkxwaves.uk',
    'routeradm.teralinkxwaves.uk',
    'radius.teralinkxwaves.uk',
    'mt.teralinkxwaves.uk',
    'prom.teralinkxwaves.uk',
    'sec.teralinkxwaves.uk',
    'lab.teralinkxwaves.uk',
    'grafana.teralinkxwaves.uk',
    'prometheus.teralinkxwaves.uk',
    'hids.teralinkxwaves.uk',
    'jupyter.teralinkxwaves.uk',
    # Legacy
    'teralinkxwaves.co.ke',
    'teralinkxwaves.spot',
    # Local
    'localhost',
    '127.0.0.1',
    'teralinkx_web',
    'web',
    # Internal IPs
    '192.168.88.108',
    '192.168.88.15',
    '192.168.88.16',
    '192.168.8.8',
    '10.0.0.1',
    '0.0.0.0',
    'prometheus',
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
    'django_redis',
    
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

# Middleware - JWT-only, CSRF not needed
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'core.middleware.last_seen_middleware.LastSeenMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'silk.middleware.SilkyMiddleware',
    'core.middleware.db_connection_middleware.DatabaseConnectionMiddleware',
]

# Security settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False       # Cloudflare handles SSL redirect
SESSION_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = [
    'https://teralinkxwaves.uk',
    'https://*.teralinkxwaves.uk',
    'https://cli.teralinkxwaves.uk',
    'https://srv.teralinkxwaves.uk',
    'https://su.teralinkxwaves.uk',
    'https://accounts.teralinkxwaves.uk',
    'https://service.teralinkxwaves.uk',
    'https://router.teralinkxwaves.uk',
    'https://mt.teralinkxwaves.uk',
    'https://prom.teralinkxwaves.uk',
    'https://sec.teralinkxwaves.uk',
    'https://lab.teralinkxwaves.uk',
]

# Session settings
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_NAME = 'sessionid'
SESSION_COOKIE_AGE = 1209600
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_SAVE_EVERY_REQUEST = False
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
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Database - PostgreSQL for production with TimescaleDB support
if dj_database_url:
    DATABASES = {
        'default': dj_database_url.config(
            default='postgres://teralinkx:justboot@192.168.88.16:5432/teralinkx',
            conn_max_age=60,
            conn_health_checks=True,
            ssl_require=False
        ),
        'timescale': dj_database_url.config(
            default='postgres://teralinkx:justboot@192.168.88.16:5432/teralinkx',
            conn_max_age=60,
            conn_health_checks=True,
            ssl_require=False
        )
    }
    # Add connection timeout and statement timeout
    for db in ['default', 'timescale']:
        DATABASES[db]['OPTIONS'] = {
            'connect_timeout': 10,
            'options': '-c statement_timeout=30000 -c idle_in_transaction_session_timeout=60000',
        }
        DATABASES[db].setdefault('CONN_MAX_AGE', 60)
        DATABASES[db].setdefault('ATOMIC_REQUESTS', False)
else:
    # Fallback database configuration
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'teralinkx',
            'USER': 'teralinkx',
            'PASSWORD': 'justboot',
            'HOST': '192.168.88.16',
            'PORT': '5432',
        },
        'timescale': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'teralinkx',
            'USER': 'teralinkx',
            'PASSWORD': 'justboot',
            'HOST': '192.168.88.16',
            'PORT': '5432',
        }
    }

# Database router for TimescaleDB gradual migration
DATABASE_ROUTERS = ['apps.finance.timescale_router.TimescaleDBRouter']

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

# JWT Configuration with persistent secret and resilience features
from datetime import timedelta
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': jwt_secret,
    'TOKEN_VERSION': jwt_version,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    # Resilience settings
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=30),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=7),
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

###############################################################
##################### CORS Configuration ######################
# Production CORS settings
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    # Production
    'https://teralinkxwaves.uk',
    'https://cli.teralinkxwaves.uk',
    'https://srv.teralinkxwaves.uk',
    'https://su.teralinkxwaves.uk',
    'https://service.teralinkxwaves.uk',
    'https://account.teralinkxwaves.uk',
    'https://accounts.teralinkxwaves.uk',
    'https://adm.teralinkxwaves.uk',
    'https://router.teralinkxwaves.uk',
    'https://routeradm.teralinkxwaves.uk',
    'https://radius.teralinkxwaves.uk',
    'https://mt.teralinkxwaves.uk',
    'https://prom.teralinkxwaves.uk',
    'https://sec.teralinkxwaves.uk',
    'https://lab.teralinkxwaves.uk',
    'https://grafana.teralinkxwaves.uk',
    'https://prometheus.teralinkxwaves.uk',
    'https://hids.teralinkxwaves.uk',
    'https://jupyter.teralinkxwaves.uk',
    # Legacy
    'https://teralinkxwaves.co.ke',
    'http://teralinkxwaves.spot',
    # Local dev
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

CORS_ALLOWED_ORIGIN_REGEXES = [
    r'^https://.*\.teralinkxwaves\.uk$',
]

CORS_ALLOW_CREDENTIALS = True

# Expose headers to frontend
CORS_EXPOSE_HEADERS = [
    'Content-Range',
    'X-Content-Range',
    'X-Session-ID',
    'X-Client-Version',
    'X-Backend-Version',
    'X-Token-Version',
]
CORS_ALLOW_HEADERS = list(default_headers) + [
    'authorization',
    'content-type',
    'x-client-timestamp',
    'x-session-id',
    'x-client-version',
    'x-hotspot-name',
    'x-device-mac',
    'x-device-ip',
    'x-backend-version',
    'x-token-version',
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

# Cache - Redis for production with connection pooling and session backup
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 50,
                "retry_on_timeout": True,
                "socket_keepalive": True,
            },
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": "teralinkx",
        "TIMEOUT": 300,
    },
    "sessions": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 20,
                "retry_on_timeout": True,
                "socket_keepalive": True,
            },
            "SOCKET_CONNECT_TIMEOUT": 5,
            "SOCKET_TIMEOUT": 5,
            "IGNORE_EXCEPTIONS": True,
        },
        "KEY_PREFIX": "teralinkx_sessions",
        "TIMEOUT": 86400,  # 24 hours
    }
}

# Celery Configuration - Docker optimized with connection management
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'

# Redis connection pool for Celery
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_RETRY = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10
CELERY_REDIS_MAX_CONNECTIONS = 50
CELERY_BROKER_POOL_LIMIT = 50

# Task timeout and cleanup settings
CELERY_TASK_SOFT_TIME_LIMIT = 300  # 5 minutes soft limit
CELERY_TASK_TIME_LIMIT = 600       # 10 minutes hard limit
CELERY_TASK_ACKS_LATE = True       # Acknowledge after task completion
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # Process one task at a time
CELERY_TASK_REJECT_ON_WORKER_LOST = False  # Don't revoke tasks on worker loss

# Result backend cleanup
CELERY_RESULT_EXPIRES = 3600        # Results expire after 1 hour
CELERY_TASK_RESULT_EXPIRES = 3600   # Task results expire after 1 hour
CELERY_RESULT_BACKEND_ALWAYS_RETRY = True
CELERY_RESULT_BACKEND_MAX_RETRIES = 10

# Database connection management for Celery
CELERY_WORKER_MAX_TASKS_PER_CHILD = 100  # Restart worker after 100 tasks to prevent leaks
CELERY_WORKER_DISABLE_RATE_LIMITS = False

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
        'teralinkx.jwt_manager': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
} 

# ============================================================================
# RADIUS API CONFIGURATION
# ============================================================================
RADIUS_API_URL = 'http://radiusapi:8010/api'

# ============================================================================
# AUTH RESILIENCE CONFIGURATION
# ============================================================================
# Backend version for frontend compatibility checks
BACKEND_VERSION = f"teralinkx-{jwt_version}"

# Token health check settings
TOKEN_HEALTH_CHECK_ENABLED = True
TOKEN_HEALTH_CHECK_INTERVAL = 60  # seconds

# Session backup settings
SESSION_BACKUP_ENABLED = True
SESSION_BACKUP_RETENTION = 86400  # 24 hours