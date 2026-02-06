"""
统计 Celery 任务

异步生成统计数据、清理历史数据等
"""

import logging
from datetime import datetime, timedelta
from celery import shared_task
from celery.utils.log import get_task_logger
from django.db.models import Count, Sum, Q
from django.utils import timezone

from articles.models import Article
from users.models import User
from comments.models import Comment
from .models import DailyStats, ArticleStats, PopularArticles

logger = get_task_logger(__name__)


@shared_task
def generate_daily_statistics(date: Optional[str] = None):
    """
    生成每日统计数据

    Args:
        date: 日期字符串 (YYYY-MM-DD)，默认为昨天

    Returns:
        dict: 统计结果
    """
    if date:
        target_date = datetime.strptime(date, '%Y-%m-%d').date()
    else:
        target_date = (timezone.now() - timedelta(days=1)).date()

    # 时间范围
    day_start = timezone.make_aware(
        timezone.datetime(target_date.year, target_date.month, target_date.day)
    )
    day_end = day_start + timedelta(days=1)

    try:
        # 获取或创建统计记录
        stats, created = DailyStats.objects.get_or_create(
            date=target_date,
            defaults={
                'articles_published': 0,
                'articles_draft': 0,
                'articles_created': 0,
                'users_new': 0,
                'users_total': 0,
                'comments_new': 0,
                'comments_total': 0,
                'views_total': 0,
                'views_unique': 0,
                'likes_total': 0,
            }
        )

        # 统计文章
        stats.articles_published = Article.objects.filter(status='published').count()
        stats.articles_draft = Article.objects.filter(status='draft').count()
        stats.articles_created = Article.objects.filter(
            created_at__gte=day_start,
            created_at__lt=day_end
        ).count()

        # 统计用户
        stats.users_new = User.objects.filter(
            created_at__gte=day_start,
            created_at__lt=day_end
        ).count()
        stats.users_total = User.objects.count()

        # 统计评论
        stats.comments_new = Comment.objects.filter(
            created_at__gte=day_start,
            created_at__lt=day_end
        ).count()
        stats.comments_total = Comment.objects.filter(status='approved').count()

        # 统计访问量
        from articles.models import ArticleView
        views_data = ArticleView.objects.filter(
            created_at__gte=day_start,
            created_at__lt=day_end
        ).aggregate(
            total_views=Count('id'),
            unique_views=Count('ip_address', distinct=True)
        )
        stats.views_total = views_data['total_views'] or 0
        stats.views_unique = views_data['unique_views'] or 0

        # 统计点赞
        from articles.models import ArticleLike
        stats.likes_total = ArticleLike.objects.count()

        stats.save()

        logger.info(f"已生成 {target_date} 的统计数据")

        return {
            'date': target_date.isoformat(),
            'created': created,
            'stats': {
                'articles_published': stats.articles_published,
                'users_new': stats.users_new,
                'comments_new': stats.comments_new,
                'views_total': stats.views_total,
            }
        }

    except Exception as e:
        logger.error(f"生成 {target_date} 统计数据失败: {e}")
        raise


@shared_task
def generate_statistics_for_date_range(start_date: str, end_date: str):
    """
    生成日期范围内的统计数据

    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)

    Returns:
        dict: 生成结果
    """
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()

    results = []
    current_date = start

    while current_date <= end:
        result = generate_daily_statistics(current_date.isoformat())
        results.append(result)
        current_date += timedelta(days=1)

    return {
        'start_date': start_date,
        'end_date': end_date,
        'total_days': len(results),
        'results': results
    }


@shared_task
def update_article_stats(article_id: int):
    """
    更新单篇文章的统计信息

    Args:
        article_id: 文章 ID
    """
    try:
        article = Article.objects.get(id=article_id)

        # 获取或创建统计
        stats, created = ArticleStats.objects.get_or_create(
            article=article,
            defaults={
                'view_count': article.view_count,
                'like_count': article.like_count,
                'comment_count': article.comment_count,
            }
        )

        # 更新统计
        if not created:
            stats.view_count = article.view_count
            stats.like_count = article.like_count
            stats.comment_count = article.comment_count
            stats.calculate_hot_score()

        logger.info(f"已更新文章 {article_id} 的统计数据")

        return True

    except Article.DoesNotExist:
        logger.warning(f"文章 {article_id} 不存在")
        return False

    except Exception as e:
        logger.error(f"更新文章 {article_id} 统计失败: {e}")
        return False


@shared_task
def batch_update_article_stats(article_ids: list):
    """
    批量更新文章统计

    Args:
        article_ids: 文章 ID 列表
    """
    updated = 0
    failed = 0

    for article_id in article_ids:
        if update_article_stats(article_id):
            updated += 1
        else:
            failed += 1

    logger.info(f"批量更新完成: {updated} 成功, {failed} 失败")

    return {
        'total': len(article_ids),
        'updated': updated,
        'failed': failed
    }


@shared_task
def cleanup_old_stats(days: int = 90):
    """
    清理旧的统计数据

    Args:
        days: 保留最近的天数
    """
    cutoff_date = timezone.now() - timedelta(days=days)

    try:
        # 删除旧的每日统计
        deleted = DailyStats.objects.filter(date__lt=cutoff_date).delete()[0]

        logger.info(f"已清理 {deleted} 条 {days} 天前的统计数据")

        return {
            'status': 'success',
            'deleted': deleted,
            'cutoff_date': cutoff_date.isoformat()
        }

    except Exception as e:
        logger.error(f"清理旧统计数据失败: {e}")
        return {
            'status': 'error',
            'message': str(e)
        }


@shared_task
def sync_popular_articles_cache():
    """
    同步热门文章缓存

    更新不同时间段的热门文章列表
    """
    try:
        # 定义时间段
        periods = {
            'daily': timedelta(days=1),
            'weekly': timedelta(days=7),
            'monthly': timedelta(days=30),
            'all_time': None
        }

        results = {}

        for period_name, period_delta in periods.items():
            # 构建查询
            queryset = Article.objects.filter(status='published')

            if period_delta:
                cutoff_time = timezone.now() - period_delta
                queryset = queryset.filter(published_at__gte=cutoff_time)

            # 获取热门文章 ID（按阅读量和点赞数排序）
            article_ids = list(
                queryset.annotate(
                    hot_score=Count('views') * 1 + Count('likes') * 5
                )
                .order_by('-hot_score', '-published_at')
                .values_list('id', flat=True)[:20]
            )

            # 更新缓存
            popular, created = PopularArticles.objects.get_or_create(
                period=period_name
            )

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


from typing import Optional
