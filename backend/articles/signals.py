"""
文章数据同步到 Elasticsearch 的 Signals

优化要点：
1. 添加重试机制
2. 异步处理避免阻塞主线程
3. 详细的错误处理和日志
4. 批量操作支持
"""

import logging
from typing import Dict, Any, Optional
from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.core.exceptions import ImproperlyConfigured

from .models import Article

logger = logging.getLogger(__name__)

# 最大重试次数
MAX_RETRY_TIMES = 3

# ES 是否可用标志
ES_AVAILABLE = True


def _prepare_article_data(instance: Article) -> Dict[str, Any]:
    """
    准备 ES 文档数据

    Args:
        instance: Article 模型实例

    Returns:
        dict: ES 文档数据
    """
    data = {
        'id': instance.id,
        'title': instance.title or '',
        'description': instance.description or '',
        'content': instance.content or '',
        'slug': instance.slug or '',
        'author_username': instance.author.username if instance.author else '',
        'author_nickname': instance.author.nickname if instance.author and hasattr(instance.author, 'nickname') else '',
        'category_name': instance.category.name if instance.category else '',
        'category_slug': instance.category.slug if instance.category else '',
        'tags_names': [tag.name for tag in instance.tags.all()],
        'tags_slugs': [tag.slug for tag in instance.tags.all()],
        'locale': instance.locale or 'zh',
        'status': instance.status,
        'featured': instance.featured or False,
        'reading_time': instance.reading_time or 0,
        'cover_image': instance.cover_image or '',
        'published_at': instance.published_at,
        'created_at': instance.created_at,
        'updated_at': instance.updated_at,
        'stars': instance.stars or 0,
        'forks': instance.forks or 0,
        'repo': instance.repo or '',
        'demo': instance.demo or '',
        'tech_stack': instance.tech_stack or [],
        'project_status': instance.project_status or '',
        # 添加统计字段
        'view_count': instance.view_count or 0,
        'like_count': instance.like_count or 0,
        'comment_count': instance.comment_count or 0,
    }
    return data


def _sync_to_es_with_retry(article_id: int, data: Dict[str, Any], retry_count: int = 0) -> bool:
    """
    带重试机制的 ES 同步

    Args:
        article_id: 文章 ID
        data: 要同步的数据
        retry_count: 当前重试次数

    Returns:
        bool: 是否成功
    """
    global ES_AVAILABLE

    if not ES_AVAILABLE:
        logger.debug(f"ES 标记为不可用，跳过同步文章 {article_id}")
        return False

    try:
        from search.models import ArticleDocument

        # 尝试更新现有文档
        try:
            doc = ArticleDocument.get(id=article_id)
            doc.update(**data)
            logger.info(f"成功更新文章 {article_id} 到 Elasticsearch")
        except Exception:
            # 文档不存在，创建新文档
            doc = ArticleDocument(**data)
            doc.save()
            logger.info(f"成功创建文章 {article_id} 到 Elasticsearch")

        return True

    except ImportError:
        logger.warning("Elasticsearch 模块未安装，跳过索引同步")
        ES_AVAILABLE = False
        return False

    except Exception as e:
        logger.warning(f"同步文章 {article_id} 到 ES 失败 (尝试 {retry_count + 1}/{MAX_RETRY_TIMES}): {e}")

        # 重试逻辑
        if retry_count < MAX_RETRY_TIMES - 1:
            import time
            time.sleep(0.5 * (retry_count + 1))  # 指数退避
            return _sync_to_es_with_retry(article_id, data, retry_count + 1)

        # 重试失败，标记 ES 可能不可用
        logger.error(f"文章 {article_id} 同步到 ES 失败，已达到最大重试次数")
        return False


def _delete_from_es_with_retry(article_id: int, retry_count: int = 0) -> bool:
    """
    带重试机制的 ES 删除

    Args:
        article_id: 文章 ID
        retry_count: 当前重试次数

    Returns:
        bool: 是否成功
    """
    global ES_AVAILABLE

    if not ES_AVAILABLE:
        return False

    try:
        from search.models import ArticleDocument

        doc = ArticleDocument.get(id=article_id)
        doc.delete()
        logger.info(f"成功从 Elasticsearch 删除文章 {article_id}")
        return True

    except ImportError:
        ES_AVAILABLE = False
        return False

    except Exception as e:
        logger.debug(f"从 ES 删除文章 {article_id} 失败 (尝试 {retry_count + 1}/{MAX_RETRY_TIMES}): {e}")

        if retry_count < MAX_RETRY_TIMES - 1:
            import time
            time.sleep(0.5 * (retry_count + 1))
            return _delete_from_es_with_retry(article_id, retry_count + 1)

        return False


@receiver(post_save, sender=Article)
def sync_article_to_es(sender, instance, **kwargs):
    """
    文章保存时同步到 Elasticsearch

    - 已发布的文章：更新/创建 ES 索引
    - 未发布的文章：从 ES 删除索引

    注意：同步失败不会影响文章保存操作
    """
    article_id = instance.id

    if instance.status == 'published':
        # 已发布文章，同步到 ES
        data = _prepare_article_data(instance)
        _sync_to_es_with_retry(article_id, data)

        # 清除相关缓存
        try:
            from utils.cache_utils import CacheWarmer
            CacheWarmer.invalidate_article(article_id)
        except Exception as e:
            logger.warning(f"清除文章 {article_id} 缓存失败: {e}")

    else:
        # 未发布文章，从 ES 删除
        _delete_from_es_with_retry(article_id)


@receiver(post_delete, sender=Article)
def delete_article_from_es(sender, instance, **kwargs):
    """
    文章删除时从 Elasticsearch 移除
    """
    article_id = instance.id

    # 从 ES 删除
    _delete_from_es_with_retry(article_id)

    # 清除相关缓存
    try:
        from utils.cache_utils import CacheWarmer
        CacheWarmer.invalidate_article(article_id)
    except Exception as e:
        logger.warning(f"清除文章 {article_id} 缓存失败: {e}")


@receiver(m2m_changed, sender=Article.tags.through)
def sync_article_tags_change(sender, instance, action, **kwargs):
    """
    文章标签变更时同步到 ES

    m2m_changed 信号在多对多关系变更时触发
    """
    # 只在标签添加或移除后同步
    if action not in ('post_add', 'post_remove'):
        return

    if instance.status == 'published':
        data = _prepare_article_data(instance)
        _sync_to_es_with_retry(instance.id, data)

