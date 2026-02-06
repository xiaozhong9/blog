"""
测试 Celery 任务执行
"""
import os
import django
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from articles.tasks import warm_article_cache, calculate_article_hot_scores
from stats.tasks import generate_daily_statistics, sync_popular_articles_cache

print("=" * 50)
print("Testing Celery Tasks")
print("=" * 50)

# 测试 1: 缓存预热
print("\n[Test 1] Cache Warming Task")
try:
    result = warm_article_cache.delay()
    print(f"[OK] Task submitted: {result.id}")
    print(f"    Status: {result.status}")

    # 等待几秒检查状态
    time.sleep(3)
    result.refresh()
    print(f"    Updated status: {result.status}")

    if result.ready():
        print(f"    Result: {result.result}")
except Exception as e:
    print(f"[ERROR] {e}")

# 测试 2: 热度分数计算
print("\n[Test 2] Hot Score Calculation")
try:
    result = calculate_article_hot_scores.delay()
    print(f"[OK] Task submitted: {result.id}")

    time.sleep(3)
    result.refresh()
    print(f"    Status: {result.status}")

    if result.ready():
        print(f"    Result: {result.result}")
except Exception as e:
    print(f"[ERROR] {e}")

# 测试 3: 每日统计生成
print("\n[Test 3] Daily Statistics Generation")
try:
    result = generate_daily_statistics.delay()
    print(f"[OK] Task submitted: {result.id}")

    time.sleep(5)
    result.refresh()
    print(f"    Status: {result.status}")

    if result.ready():
        print(f"    Result: {result.result}")
except Exception as e:
    print(f"[ERROR] {e}")

# 测试 4: 热门文章缓存同步
print("\n[Test 4] Popular Articles Cache Sync")
try:
    result = sync_popular_articles_cache.delay()
    print(f"[OK] Task submitted: {result.id}")

    time.sleep(3)
    result.refresh()
    print(f"    Status: {result.status}")

    if result.ready():
        print(f"    Result: {result.result}")
except Exception as e:
    print(f"[ERROR] {e}")

print("\n" + "=" * 50)
print("Tests Completed!")
print("=" * 50)
print("\nTips:")
print("- Check Celery Worker terminal for detailed logs")
print("- Visit http://localhost:5555 for Flower monitoring")
print("- Tasks will run automatically based on schedule:")
print("    * Daily Statistics: 00:00 every day")
print("    * Clean Cache: Every hour")
print("    * Popular Articles: Every 15 minutes")

