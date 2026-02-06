"""
Django 基础配置
包含所有环境共享的配置项
"""

import os
from pathlib import Path
from datetime import timedelta
from celery.schedules import crontab
from decouple import config, Csv

# ============================================
# 基础路径配置
# ============================================
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ============================================
# 核心配置
# ============================================
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-this-in-production')
DEBUG = config('DEBUG', default=True, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# 站点信息
SITE_URL = config('SITE_URL', default='http://localhost:8000')
SITE_NAME = config('SITE_NAME', default='Nano Banana Blog')

# ============================================
# 应用配置
# ============================================
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'drf_yasg',
    'django_celery_beat',
    'django_celery_results',
]

LOCAL_APPS = [
    'users.apps.UsersConfig',
    'articles.apps.ArticlesConfig',
    'categories.apps.CategoriesConfig',
    'tags.apps.TagsConfig',
    'comments.apps.CommentsConfig',
    'search.apps.SearchConfig',  # Elasticsearch 搜索
    'stats.apps.StatsConfig',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# ============================================
# 中间件配置
# ============================================
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # CORS 中间件
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

# ============================================
# 模板配置
# ============================================
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

WSGI_APPLICATION = 'config.wsgi.application'

# ============================================
# 数据库配置 (MySQL)
# ============================================
DATABASES = {
    'default': {
        'ENGINE': config('DB_ENGINE', default='django.db.backends.mysql'),
        'NAME': config('DB_NAME', default='nano_banana_db'),
        'USER': config('DB_USER', default='root'),
        'PASSWORD': config('DB_PASSWORD', default='admin'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# ============================================
# 缓存配置 (Redis)
# ============================================
# Redis 连接池配置
REDIS_CONNECTION_POOL_KWARGS = {
    'max_connections': config('REDIS_MAX_CONNECTIONS', default=50, cast=int),
    'retry_on_timeout': True,
    'socket_keepalive': True,
    'socket_keepalive_options': {},
}

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{config('REDIS_HOST', default='localhost')}:{config('REDIS_PORT', default='6379')}/{config('REDIS_DB', default='0')}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': config('REDIS_PASSWORD', default=''),
            # 使用 Hiredis 解析器（如果可用）以获得更好的性能
            'PARSER_CLASS': 'redis.connection.HiredisParser' if config('USE_HIREDIS', default=False, cast=bool) else 'redis.connection.PythonParser',
            # 连接超时设置
            'SOCKET_CONNECT_TIMEOUT': config('REDIS_CONNECT_TIMEOUT', default=5, cast=int),
            'SOCKET_TIMEOUT': config('REDIS_SOCKET_TIMEOUT', default=5, cast=int),
            # 连接池配置
            'CONNECTION_POOL_KWARGS': REDIS_CONNECTION_POOL_KWARGS,
        },
        'KEY_PREFIX': config('REDIS_CACHE_PREFIX', default='banana_cache'),
        'TIMEOUT': config('CACHE_DEFAULT_TIMEOUT', default=300, cast=int),  # 默认缓存 5 分钟
        'VERSION': 1,  # 缓存版本，用于批量清除缓存
    },
    # 会话缓存（单独的数据库）
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f"redis://{config('REDIS_HOST', default='localhost')}:{config('REDIS_PORT', default='6379')}/{config('REDIS_SESSION_DB', default='1')}",
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'PASSWORD': config('REDIS_PASSWORD', default=''),
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
            'CONNECTION_POOL_KWARGS': {'max_connections': 20},
        },
        'KEY_PREFIX': 'session',
        'TIMEOUT': 86400,  # 24 小时
    },
}

# 会话缓存
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# ============================================
# 密码验证
# ============================================
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# 自定义用户模型
AUTH_USER_MODEL = 'users.User'

# ============================================
# 国际化配置
# ============================================
LANGUAGE_CODE = config('LANGUAGE_CODE', default='zh-hans')
TIME_ZONE = config('TIME_ZONE', default='Asia/Shanghai')
USE_I18N = True
USE_TZ = True

# ============================================
# 静态文件配置
# ============================================
STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = BASE_DIR / config('STATIC_ROOT', default='staticfiles')
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# ============================================
# 媒体文件配置
# ============================================
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = BASE_DIR / config('MEDIA_ROOT', default='media')

# ============================================
# 默认主键类型
# ============================================
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# Django REST Framework 配置
# ============================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ),
    'DEFAULT_THROTTLE_CLASSES': (
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
    ),
    'DEFAULT_THROTTLE_RATES': {
        'anon': '20/min',  # 游客每分钟最多 20 次请求
        'user': '60/min',  # 登录用户每分钟最多 60 次请求
        'login': '5/min',  # 登录每分钟最多 5 次
        'comment': '3/hour',  # 评论每小时最多 3 条（游客）
    },
    'EXCEPTION_HANDLER': 'config.exceptions.custom_exception_handler',
}

# ============================================
# JWT 认证配置
# ============================================
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME', default=60, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(minutes=config('JWT_REFRESH_TOKEN_LIFETIME', default=10080, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': config('JWT_ALGORITHM', default='HS256'),
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# ============================================
# CORS 配置
# ============================================
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', default='http://localhost:5173,http://localhost:3000', cast=Csv())
CORS_ALLOW_CREDENTIALS = config('CORS_ALLOW_CREDENTIALS', default=True, cast=bool)

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'origin',
    'user-agent',
    'x-csrftoken',
]

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]

# ============================================
# Elasticsearch 配置
# ============================================
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': f"http://{config('ELASTICSEARCH_HOST', default='localhost')}:{config('ELASTICSEARCH_PORT', default='9200')}",
    },
}

ELASTICSEARCH_INDEX_PREFIX = config('ELASTICSEARCH_INDEX_PREFIX', default='banana_')

# ============================================
# Celery 配置
# ============================================

# Celery Redis Broker 配置
REDIS_HOST = config('REDIS_HOST', default='localhost')
REDIS_PORT = config('REDIS_PORT', default='6379')
REDIS_PASSWORD = config('REDIS_PASSWORD', default='')

# 构建连接 URL
if REDIS_PASSWORD:
    broker_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/3"
    backend_url = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/4"
else:
    broker_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/3"
    backend_url = f"redis://{REDIS_HOST}:{REDIS_PORT}/4"

CELERY_BROKER_URL = config('CELERY_BROKER_URL', default=broker_url)
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default=backend_url)

# Celery 基础配置
CELERY_TIMEZONE = config('CELERY_TIMEZONE', default='Asia/Shanghai')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = config('CELERY_TASK_TIME_LIMIT', default=30 * 60, cast=int)  # 30 分钟
CELERY_TASK_SOFT_TIME_LIMIT = config('CELERY_TASK_SOFT_TIME_LIMIT', default=25 * 60, cast=int)  # 25 分钟

# Worker 配置
CELERY_WORKER_PREFETCH_MULTIPLIER = config('CELERY_WORKER_PREFETCH_MULTIPLIER', default=4, cast=int)
CELERY_WORKER_MAX_TASKS_PER_CHILD = config('CELERY_WORKER_MAX_TASKS_PER_CHILD', default=1000, cast=int)
# CELERY_WORKER_CONCURRENCY: None 表示使用 CPU 核心数，从环境变量读取（可选）
_worker_concurrency = config('CELERY_WORKER_CONCURRENCY', default=None)
CELERY_WORKER_CONCURRENCY = int(_worker_concurrency) if _worker_concurrency else None

# 结果后端配置
CELERY_RESULT_BACKEND_TRANSPORT_OPTIONS = {
    'retry_policy': {
        'timeout': 5.0
    },
    'master_name': 'mymaster',
}

# 任务配置
CELERY_TASK_ACKS_LATE = True  # 任务完成后才确认，防止任务丢失
CELERY_TASK_REJECT_ON_WORKER_LOST = True  # Worker 丢失时拒绝任务
CELERY_TASK_SEND_SENT_EVENT = True  # 发送任务发送事件

# Beat 配置
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_BEAT_SCHEDULE = {
    # 示例：每日生成统计数据
    'generate-daily-stats': {
        'task': 'stats.tasks.generate_daily_statistics',
        'schedule': crontab(hour=0, minute=0),  # 每天 00:00
    },
    # 每小时清理过期缓存
    'clean-expired-cache': {
        'task': 'articles.tasks.clean_expired_cache',
        'schedule': crontab(minute=0),  # 每小时
    },
    # 每 15 分钟同步热门文章缓存
    'sync-popular-articles': {
        'task': 'stats.tasks.sync_popular_articles_cache',
        'schedule': crontab(minute='*/15'),  # 每 15 分钟
    },
}

# ============================================
# 日志配置
# ============================================
LOG_LEVEL = config('LOG_LEVEL', default='INFO')
LOG_DIR = BASE_DIR / config('LOG_DIR', default='logs')

# 确保日志目录存在
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{levelname}] {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {asctime} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
            'filters': ['require_debug_true'],
        },
        'file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'django.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': LOG_LEVEL,
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': LOG_LEVEL,
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}


# ============================================
# 邮件配置
# ============================================
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='localhost')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@nanobanana.dev')
SERVER_EMAIL = config('SERVER_EMAIL', default='server@nanobanana.dev')
ADMINS = [('Admin', config('ADMIN_EMAIL', default='admin@nanobanana.dev'))]

# ============================================
# 安全配置 (生产环境必须设置)
# ============================================
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# ============================================
# Giscus 评论配置
# ============================================
GISCUS_CONFIG = {
    'repo': config('GISCUS_REPO', default=''),
    'repo_id': config('GISCUS_REPO_ID', default=''),
    'category': config('GISCUS_CATEGORY', default=''),
    'category_id': config('GISCUS_CATEGORY_ID', default=''),
    'theme': config('GISCUS_THEME', default='preferred_color_scheme'),
    'lang': config('GISCUS_LANG', default='zh-CN'),
}

# ============================================
# 其他配置
# ============================================
# 上传文件限制
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB

# 表单验证
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
