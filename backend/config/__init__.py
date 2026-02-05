# 确保在 Django 启动时导入 Celery app
from .celery import app as celery_app  # noqa

__all__ = ('celery_app',)
