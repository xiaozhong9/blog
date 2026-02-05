"""
开发环境配置
"""

from .base import *

# ============================================
# 开发环境特定配置
# ============================================
DEBUG = True

# 允许的主机
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# ============================================
# 开发工具
# ============================================
INSTALLED_APPS += [
    'django_extensions',
    'debug_toolbar',
]

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

# Debug Toolbar 配置
INTERNAL_IPS = ['127.0.0.1', 'localhost']

# ============================================
# 开发环境日志
# ============================================
LOG_LEVEL = 'DEBUG'

# 暂时禁用 (待修复 LOGGING 配置)
# LOGGING['handlers']['console']['level'] = 'DEBUG'
# LOGGING['loggers']['django']['level'] = 'DEBUG'

# ============================================
# 开发环境邮件 (输出到控制台)
# ============================================
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ============================================
# 开发环境静态文件
# ============================================
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
