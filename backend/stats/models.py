"""
统计模型
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


class DailyStats(models.Model):
    """每日统计数据"""

    # 日期
    date = models.DateField(_('日期'), unique=True)

    # 文章统计
    articles_published = models.PositiveIntegerField(_('已发布文章数'), default=0)
    articles_draft = models.PositiveIntegerField(_('草稿文章数'), default=0)
    articles_created = models.PositiveIntegerField(_('新增文章数'), default=0)

    # 用户统计
    users_new = models.PositiveIntegerField(_('新增用户数'), default=0)
    users_total = models.PositiveIntegerField(_('总用户数'), default=0)

    # 评论统计
    comments_new = models.PositiveIntegerField(_('新增评论数'), default=0)
    comments_total = models.PositiveIntegerField(_('总评论数'), default=0)

    # 访问统计
    views_total = models.PositiveIntegerField(_('总访问量'), default=0)
    views_unique = models.PositiveIntegerField(_('独立访客数'), default=0)

    # 其他统计
    likes_total = models.PositiveIntegerField(_('总点赞数'), default=0)

    # 时间字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('每日统计')
        verbose_name_plural = _('每日统计')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['-date']),
        ]

    def __str__(self):
        return f'{self.date} 统计'


class ArticleStats(models.Model):
    """文章统计"""

    article = models.OneToOneField(
        'articles.Article',
        on_delete=models.CASCADE,
        related_name='stats',
        verbose_name=_('文章')
    )

    # 阅读统计
    view_count = models.PositiveIntegerField(_('阅读量'), default=0)
    view_count_unique = models.PositiveIntegerField(_('独立访客数'), default=0)

    # 互动统计
    like_count = models.PositiveIntegerField(_('点赞数'), default=0)
    comment_count = models.PositiveIntegerField(_('评论数'), default=0)
    share_count = models.PositiveIntegerField(_('分享数'), default=0)

    # 收藏统计
    bookmark_count = models.PositiveIntegerField(_('收藏数'), default=0)

    # 热度分数 (综合计算)
    hot_score = models.FloatField(_('热度分数'), default=0)

    # 最后更新时间
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('文章统计')
        verbose_name_plural = _('文章统计')
        indexes = [
            models.Index(fields=['-hot_score']),
            models.Index(fields=['-view_count']),
        ]

    def __str__(self):
        return f'{self.article.title} - 统计'

    def calculate_hot_score(self):
        """
        计算热度分数
        公式: view_count * 1 + like_count * 5 + comment_count * 10 + share_count * 20
        """
        self.hot_score = (
            self.view_count * 1 +
            self.like_count * 5 +
            self.comment_count * 10 +
            self.share_count * 20
        )
        self.save(update_fields=['hot_score'])


class PopularArticles(models.Model):
    """热门文章缓存"""

    class Period(models.TextChoices):
        DAILY = 'daily', _('每日')
        WEEKLY = 'weekly', _('每周')
        MONTHLY = 'monthly', _('每月')
        ALL_TIME = 'all_time', _('全部时间')

    period = models.CharField(
        _('周期'),
        max_length=20,
        choices=Period.choices,
        unique=True
    )

    # 存储 JSON 格式的文章 ID 列表
    article_ids = models.JSONField(_('文章 ID 列表'), default=list)

    # 缓存时间
    cached_at = models.DateTimeField(_('缓存时间'), auto_now=True)

    class Meta:
        verbose_name = _('热门文章')
        verbose_name_plural = _('热门文章')
        indexes = [
            models.Index(fields=['period']),
        ]

    def __str__(self):
        return f'{self.get_period_display()} - {len(self.article_ids)} 篇'

    def is_expired(self, hours=1):
        """检查缓存是否过期"""
        expiry_time = timezone.now() - timedelta(hours=hours)
        return self.cached_at < expiry_time


class TagStats(models.Model):
    """标签统计"""

    tag = models.OneToOneField(
        'tags.Tag',
        on_delete=models.CASCADE,
        related_name='stats',
        verbose_name=_('标签')
    )

    # 文章数
    articles_count = models.PositiveIntegerField(_('文章数'), default=0)

    # 总阅读量
    view_count = models.PositiveIntegerField(_('总阅读量'), default=0)

    # 热度分数
    hot_score = models.FloatField(_('热度分数'), default=0)

    # 更新时间
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('标签统计')
        verbose_name_plural = _('标签统计')
        indexes = [
            models.Index(fields=['-hot_score']),
            models.Index(fields=['-articles_count']),
        ]

    def __str__(self):
        return f'{self.tag.name} - 统计'


class CategoryStats(models.Model):
    """分类统计"""

    category = models.OneToOneField(
        'categories.Category',
        on_delete=models.CASCADE,
        related_name='stats',
        verbose_name=_('分类')
    )

    # 文章数
    articles_count = models.PositiveIntegerField(_('文章数'), default=0)

    # 总阅读量
    view_count = models.PositiveIntegerField(_('总阅读量'), default=0)

    # 更新时间
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('分类统计')
        verbose_name_plural = _('分类统计')
        ordering = ['-view_count']

    def __str__(self):
        return f'{self.category.name} - 统计'


class UserAction(models.Model):
    """用户行为记录"""

    class ActionType(models.TextChoices):
        VIEW_ARTICLE = 'view_article', _('浏览文章')
        LIKE_ARTICLE = 'like_article', _('点赞文章')
        BOOKMARK_ARTICLE = 'bookmark_article', _('收藏文章')
        SHARE_ARTICLE = 'share_article', _('分享文章')
        COMMENT = 'comment', _('评论')
        LIKE_COMMENT = 'like_comment', _('点赞评论')
        SEARCH = 'search', _('搜索')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions',
        verbose_name=_('用户')
    )

    # 行为类型
    action_type = models.CharField(
        _('行为类型'),
        max_length=30,
        choices=ActionType.choices
    )

    # 关联对象
    article = models.ForeignKey(
        'articles.Article',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions',
        verbose_name=_('文章')
    )

    comment = models.ForeignKey(
        'comments.Comment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions',
        verbose_name=_('评论')
    )

    # 元数据 (JSON 格式存储额外信息)
    metadata = models.JSONField(_('元数据'), blank=True, null=True)

    # IP 地址
    ip_address = models.GenericIPAddressField(_('IP 地址'), null=True, blank=True)

    # 时间字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('用户行为')
        verbose_name_plural = _('用户行为')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['action_type', '-created_at']),
            models.Index(fields=['article', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user} - {self.get_action_type_display()}'
