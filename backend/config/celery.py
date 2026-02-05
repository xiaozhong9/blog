"""
Celery 配置
"""

import os
from celery import Celery
from celery.schedules import crontab

# 设置默认 Django settings 模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')

app = Celery('nano_banana')

# 使用 Django settings 配置 Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# 自动发现所有 app 中的 tasks.py
app.autodiscover_tasks()

# 配置定时任务
app.conf.beat_schedule = {
    # 每日生成统计数据
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


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """调试任务"""
    print(f'Request: {self.request!r}')
