"""
文章数据同步到 Elasticsearch 的 Signals
"""

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Article


def _prepare_article_data(instance):
    """
    准备 ES 文档数据

    Args:
        instance: Article 模型实例

    Returns:
        dict: ES 文档数据
    """
    return {
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
    }


@receiver(post_save, sender=Article)
def sync_article_to_es(sender, instance, **kwargs):
    """
    文章保存时同步到 Elasticsearch

    - 已发布的文章：更新/创建 ES 索引
    - 未发布的文章：从 ES 删除索引
    """
    import logging
    logger = logging.getLogger(__name__)

    # 延迟导入避免循环依赖
    from search.models import ArticleDocument

    if instance.status == 'published':
        try:
            # 尝试更新现有文档
            doc = ArticleDocument.get(id=instance.id)
            doc.update(**_prepare_article_data(instance))
            logger.info(f"Successfully updated article {instance.id} in Elasticsearch")
        except Exception:
            # 文档不存在，创建新文档
            try:
                ArticleDocument(**_prepare_article_data(instance)).save()
                logger.info(f"Successfully created article {instance.id} in Elasticsearch")
            except Exception as e:
                # 记录错误但不阻止保存操作
                logger.warning(f"Failed to index article {instance.id}: {e}")
    else:
        # 从 ES 删除未发布的文章
        try:
            doc = ArticleDocument.get(id=instance.id)
            doc.delete()
            logger.info(f"Successfully deleted unpublished article {instance.id} from Elasticsearch")
        except Exception as e:
            # 文档不存在或删除失败，记录但不阻止
            logger.debug(f"Article {instance.id} not in ES or deletion failed: {e}")


@receiver(post_delete, sender=Article)
def delete_article_from_es(sender, instance, **kwargs):
    """
    文章删除时从 Elasticsearch 移除
    """
    import logging
    logger = logging.getLogger(__name__)

    from search.models import ArticleDocument

    try:
        doc = ArticleDocument.get(id=instance.id)
        doc.delete()
        logger.info(f"Successfully deleted article {instance.id} from Elasticsearch")
    except Exception as e:
        # 记录错误但不阻止删除操作
        logger.warning(f"Failed to delete article {instance.id} from Elasticsearch: {e}")
