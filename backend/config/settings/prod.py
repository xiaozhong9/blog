"""
生产环境配置
"""

from .base import *

# ============================================
# 生产环境特定配置
# ============================================
DEBUG = False

# 允许的主机 (需要配置)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# ============================================
# 安全配置
# ============================================
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# ============================================
# 生产环境日志
# ============================================
LOG_LEVEL = 'WARNING'

# 暂时禁用 (待修复 LOGGING 配置)
# LOGGING['handlers']['console']['level'] = 'WARNING'
# LOGGING['loggers']['django']['level'] = 'WARNING'

# ============================================
# 生产环境静态文件和媒体文件
# ============================================
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_ROOT = BASE_DIR / 'media'

# ============================================
# 性能优化
# ============================================
# 连接池配置
CONN_MAX_AGE = 600

# ============================================
# 监控和错误追踪 (可选)
# ============================================
# Sentry 配置
# SENTRY_DSN = config('SENTRY_DSN', default='')
# if SENTRY_DSN:
#     import sentry_sdk
#     from sentry_sdk.integrations.django import DjangoIntegration
#     sentry_sdk.init(
#         dsn=SENTRY_DSN,
#         integrations=[DjangoIntegration()],
#         traces_sample_rate=0.1,
#         send_default_pii=False
#     )
