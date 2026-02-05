"""
分类模型
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Category(models.Model):
    """文章分类模型"""

    class CategoryType(models.TextChoices):
        BLOG = 'blog', _('博客')
        PROJECTS = 'projects', _('项目')
        LIFE = 'life', _('生活')
        NOTES = 'notes', _('笔记')

    # 基础字段
    name = models.CharField(_('分类名称'), max_length=100)
    slug = models.SlugField(_('URL 标识'), max_length=100, unique=True)
    description = models.TextField(_('描述'), blank=True)
    icon = models.CharField(_('图标'), max_length=50, blank=True)

    # 类型
    category_type = models.CharField(
        _('分类类型'),
        max_length=20,
        choices=CategoryType.choices,
        default=CategoryType.BLOG
    )

    # SEO 字段
    keywords = models.CharField(_('SEO 关键词'), max_length=255, blank=True)

    # 排序
    sort_order = models.PositiveIntegerField(_('排序'), default=0)

    # 统计字段
    articles_count = models.PositiveIntegerField(_('文章数量'), default=0)

    # 时间字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('分类')
        verbose_name_plural = _('分类')
        ordering = ['sort_order', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category_type']),
            models.Index(fields=['sort_order']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """获取绝对 URL"""
        return f'/categories/{self.slug}/'
