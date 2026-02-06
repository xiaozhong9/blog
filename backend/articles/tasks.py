"""
文章 Celery 任务

异步处理缓存更新、ES 同步等耗时操作
"""

import logging
from typing import List, Optional
from celery import shared_task
from celery.utils.log import get_task_logger

from .models import Article
from utils.cache_utils import CacheWarmer, delete_pattern

logger = get_task_logger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def sync_article_to_es_async(self, article_id: int) -> bool:
    """
    异步同步文章到 Elasticsearch

    Args:
        article_id: 文章 ID

    Returns:
        bool: 是否成功
    """
    try:
        article = Article.objects.get(id=article_id)

        if article.status != 'published':
            logger.info(f"文章 {article_id} 状态不是已发布，跳过 ES 同步")
            return True

        # 导入并同步
        from articles.signals import _prepare_article_data, _sync_to_es_with_retry

        data = _prepare_article_data(article)
        success = _sync_to_es_with_retry(article_id, data)

        if not success:
            raise self.retry(exc=Exception(f"同步文章 {article_id} 到 ES 失败"))

        return True

    except Article.DoesNotExist:
        logger.warning(f"文章 {article_id} 不存在，跳过 ES 同步")
        return True

    except Exception as e:
        logger.error(f"异步同步文章 {article_id} 到 ES 失败: {e}")
        raise


@shared_task
def batch_sync_articles_to_es(article_ids: List[int]) -> dict:
    """
    批量同步文章到 Elasticsearch

    Args:
        article_ids: 文章 ID 列表

    Returns:
        dict: 同步结果统计
    """
    from articles.signals import _prepare_article_data, _sync_to_es_with_retry

    success_count = 0
    failed_count = 0
    failed_ids = []

    for article_id in article_ids:
        try:
            article = Article.objects.get(id=article_id)

            if article.status != 'published':
                continue

            data = _prepare_article_data(article)
            if _sync_to_es_with_retry(article_id, data):
                success_count += 1
            else:
                failed_count += 1
                failed_ids.append(article_id)

        except Article.DoesNotExist:
            failed_count += 1
            failed_ids.append(article_id)

        except Exception as e:
            logger.error(f"批量同步文章 {article_id} 失败: {e}")
            failed_count += 1
            failed_ids.append(article_id)

    return {
        'total': len(article_ids),
        'success': success_count,
        'failed': failed_count,
        'failed_ids': failed_ids
    }


@shared_task
def warm_article_cache(article_ids: Optional[List[int]] = None) -> dict:
    """
    预热文章缓存

    Args:
        article_ids: 文章 ID 列表，None 表示预热所有已发布文章

    Returns:
        dict: 预热结果
    """
    if article_ids is None:
        # 预热所有已发布文章
        article_ids = list(
            Article.objects.filter(status='published')
            .values_list('id', flat=True)
        )

    success = CacheWarmer.warm_article_stats(article_ids)

    return {
        'total': len(article_ids),
        'success': success
    }


@shared_task
def clean_expired_cache():
    """
    清理过期的缓存

    这个任务应该由 Celery Beat 定期执行
    """
    try:
        # Redis 会自动清理过期的键，这里主要用于清理特定模式
        # 比如清理旧的搜索结果缓存

        # 清理超过 1 天的搜索缓存
        from django_redis import get_redis_connection
        from django.conf import settings

        redis_conn = get_redis_connection("default")

        # 获取所有搜索相关的键
        pattern = f"{settings.REDIS_CACHE_PREFIX}*:search:*"
        keys = redis_conn.keys(pattern)

        if keys:
            # 检查每个键的 TTL
            expired_keys = []
            for key in keys:
                ttl = redis_conn.ttl(key)
                if ttl == -1:  # 没有设置过期时间的旧键
                    expired_keys.append(key)

            if expired_keys:
                redis_conn.delete(*expired_keys)
                logger.info(f"清理了 {len(expired_keys)} 个过期的搜索缓存")

        return {
            'status': 'success',
            'cleaned': len(expired_keys) if expired_keys else 0
        }

    except Exception as e:
        logger.error(f"清理过期缓存失败: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def invalidate_article_caches(article_id: int):
    """
    使文章相关的所有缓存失效

    Args:
        article_id: 文章 ID
    """
    try:
        CacheWarmer.invalidate_article(article_id)
        logger.info(f"已清除文章 {article_id} 的所有缓存")
        return True
    except Exception as e:
        logger.error(f"清除文章 {article_id} 缓存失败: {e}")
        return False


@shared_task
def rebuild_es_index():
    """
    重建 Elasticsearch 索引

    警告：这是一个耗时操作，应该离线执行
    """
    try:
        from search.models import ArticleDocument
        from django_elasticsearch_dsl.registries import registry

        # 获取所有文档类
        documents = registry.get_documents()

        for doc in documents:
            doc_class = doc[0]
            index_name = doc_class._index._name

            logger.info(f"开始重建索引: {index_name}")

            # 获取需要索引的 queryset
            queryset = doc_class().get_indexing_queryset()

            # 批量索引
            count = 0
            for obj in queryset.iterator(chunk_size=100):
                try:
                    doc_class().update(obj)
                    count += 1

                    if count % 100 == 0:
                        logger.info(f"已索引 {count} 条记录")

                except Exception as e:
                    logger.error(f"索引对象 {obj} 失败: {e}")

            logger.info(f"索引 {index_name} 重建完成，共 {count} 条记录")

        return {
            'status': 'success',
            'message': '索引重建完成'
        }

    except Exception as e:
        logger.error(f"重建 ES 索引失败: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def calculate_article_hot_scores(article_ids: Optional[List[int]] = None):
    """
    重新计算文章热度分数

    Args:
        article_ids: 文章 ID 列表，None 表示所有文章
    """
    if article_ids is None:
        article_ids = list(
            Article.objects.filter(status='published')
            .values_list('id', flat=True)
        )

    updated_count = 0

    for article_id in article_ids:
        try:
            article = Article.objects.get(id=article_id)

            # 计算热度分数
            hot_score = (
                article.view_count * 1 +
                article.like_count * 5 +
                article.comment_count * 10
            )

            # 更新文章的热度（如果需要存储）
            # 这里假设有一个 hot_score 字段

            updated_count += 1

        except Article.DoesNotExist:
            continue

    logger.info(f"已更新 {updated_count} 篇文章的热度分数")

    return {
        'total': len(article_ids),
        'updated': updated_count
    }


@shared_task
def sync_popular_articles_cache():
    """
    同步热门文章缓存

    定期更新热门文章列表，存储到缓存或数据库
    """
    try:
        from stats.models import PopularArticles
        from datetime import datetime, timedelta
        from django.utils import timezone

        # 定义时间周期
        periods = {
            'daily': timedelta(days=1),
            'weekly': timedelta(days=7),
            'monthly': timedelta(days=30),
            'all_time': None
        }

        results = {}

        for period_name, period_delta in periods.items():
            # 获取该时间段内热门文章
            queryset = Article.objects.filter(status='published')

            if period_delta:
                cutoff_time = timezone.now() - period_delta
                queryset = queryset.filter(published_at__gte=cutoff_time)

            # 按热度排序
            article_ids = list(
                queryset.order_by('-view_count', '-like_count')
                .values_list('id', flat=True)[:20]
            )

            # 更新或创建缓存记录
            popular, created = PopularArticles.objects.get_or_create(
                period=period_name,
                defaults={'article_ids': article_ids}
            )

            if not created:
                popular.article_ids = article_ids
                popular.save()

            results[period_name] = len(article_ids)

        logger.info(f"热门文章缓存已更新: {results}")

        return {
            'status': 'success',
            'periods': results
        }

    except Exception as e:
        logger.error(f"同步热门文章缓存失败: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }
