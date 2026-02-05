"""
标签模型
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Tag(models.Model):
    """文章标签模型"""

    # 基础字段
    name = models.CharField(_('标签名称'), max_length=100, unique=True)
    slug = models.SlugField(_('URL 标识'), max_length=100, unique=True)
    description = models.TextField(_('描述'), blank=True)

    # SEO 字段
    keywords = models.CharField(_('SEO 关键词'), max_length=255, blank=True)

    # 统计字段
    articles_count = models.PositiveIntegerField(_('文章数量'), default=0)

    # 颜色 (用于前端展示)
    color = models.CharField(_('颜色'), max_length=20, blank=True)

    # 时间字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('标签')
        verbose_name_plural = _('标签')
        ordering = ['-articles_count', 'name']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['name']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """获取绝对 URL"""
        return f'/tags/{self.slug}/'
