"""
工具模块配置
"""

from django.apps import AppConfig


class UtilsConfig(AppConfig):
    """工具模块应用配置"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'utils'
    verbose_name = '工具模块'
