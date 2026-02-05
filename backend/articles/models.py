"""
文章模型
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db.models import Q


class Article(models.Model):
    """文章模型"""

    class ArticleStatus(models.TextChoices):
        DRAFT = 'draft', _('草稿')
        PUBLISHED = 'published', _('已发布')
        ARCHIVED = 'archived', _('已归档')

    # 基础字段
    title = models.CharField(_('标题'), max_length=500)
    slug = models.SlugField(_('URL 标识'), max_length=200, unique=True)
    description = models.TextField(_('描述'), max_length=1000)
    content = models.TextField(_('内容'), blank=True)

    # 作者
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='articles',
        verbose_name=_('作者')
    )

    # 分类
    category = models.ForeignKey(
        'categories.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name=_('分类')
    )

    # 标签 (多对多)
    tags = models.ManyToManyField(
        'tags.Tag',
        blank=True,
        related_name='articles',
        verbose_name=_('标签')
    )

    # 语言
    locale = models.CharField(
        _('语言'),
        max_length=5,
        choices=[('zh', _('中文')), ('en', _('英文'))],
        default='zh'
    )

    # 阅读时间 (分钟)
    reading_time = models.PositiveIntegerField(_('阅读时间'), default=0)

    # 状态
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT
    )

    # 是否精选
    featured = models.BooleanField(_('精选'), default=False)

    # 封面图
    cover_image = models.URLField(_('封面图'), blank=True)

    # SEO 字段
    keywords = models.CharField(_('SEO 关键词'), max_length=255, blank=True)

    # 统计字段
    view_count = models.PositiveIntegerField(_('阅读量'), default=0)
    like_count = models.PositiveIntegerField(_('点赞数'), default=0)
    comment_count = models.PositiveIntegerField(_('评论数'), default=0)

    # 项目专属字段
    stars = models.PositiveIntegerField(_('Stars'), default=0, null=True, blank=True)
    forks = models.PositiveIntegerField(_('Forks'), default=0, null=True, blank=True)
    repo = models.URLField(_('仓库地址'), blank=True)
    demo = models.URLField(_('演示地址'), blank=True)
    tech_stack = models.JSONField(_('技术栈'), blank=True, null=True)
    project_status = models.CharField(
        _('项目状态'),
        max_length=20,
        choices=[
            ('active', _('活跃')),
            ('maintenance', _('维护中')),
            ('archived', _('已归档')),
        ],
        blank=True
    )

    # 时间字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    published_at = models.DateTimeField(_('发布时间'), null=True, blank=True)

    class Meta:
        verbose_name = _('文章')
        verbose_name_plural = _('文章')
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['featured']),
            models.Index(fields=['locale']),
            models.Index(fields=['-published_at']),
            models.Index(fields=['-view_count']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 自动生成 slug (如果未提供)
        if not self.slug and self.title:
            self.slug = slugify(self.title)

        # 自动计算阅读时间
        if self.content and not self.reading_time:
            self.reading_time = self.calculate_reading_time()

        super().save(*args, **kwargs)

    def calculate_reading_time(self):
        """
        计算文章阅读时间（分钟）
        支持中英文混合内容
        """
        import re

        if not self.content:
            return 1

        # 移除 HTML 标签
        content = re.sub(r'<[^>]+>', ' ', self.content)
        # 移除代码块
        content = re.sub(r'<code[^>]*>.*?</code>', ' ', content, flags=re.DOTALL)
        content = re.sub(r'<pre[^>]*>.*?</pre>', ' ', content, flags=re.DOTALL)

        # 移除多余的空白字符
        content = re.sub(r'\s+', ' ', content).strip()

        # 统计中文字符（包括 CJK 统一汉字）
        chinese_chars = re.findall(r'[\u4e00-\u9fa5]', content)
        chinese_count = len(chinese_chars)

        # 统计英文单词（移除中文字符后按空格分词）
        english_text = re.sub(r'[\u4e00-\u9fa5]', ' ', content)
        english_words = re.findall(r'\b[a-zA-Z]+\b', english_text)
        english_count = len(english_words)

        # 阅读速度：中文 400字/分钟，英文 225词/分钟
        chinese_time = chinese_count / 400
        english_time = english_count / 225

        # 总时间（至少 1 分钟）
        total_time = chinese_time + english_time
        return max(1, int(total_time) + (1 if total_time % 1 >= 0.5 else 0))

    def get_absolute_url(self):
        """获取绝对 URL"""
        return f'/articles/{self.slug}/'

    @property
    def is_published(self):
        """是否已发布"""
        return self.status == self.ArticleStatus.PUBLISHED

    @property
    def is_draft(self):
        """是否是草稿"""
        return self.status == self.ArticleStatus.DRAFT

    @property
    def category_type(self):
        """获取分类类型 (便捷方法)"""
        return self.category.category_type if self.category else 'blog'


class ArticleView(models.Model):
    """文章阅读记录 (用于异步统计)"""

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='views',
        verbose_name=_('文章')
    )
    ip_address = models.GenericIPAddressField(_('IP 地址'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)

    # 时间字段
    created_at = models.DateTimeField(_('访问时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('阅读记录')
        verbose_name_plural = _('阅读记录')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', '-created_at']),
        ]


class ArticleLike(models.Model):
    """文章点赞记录"""

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('文章')
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='article_likes',
        verbose_name=_('用户'),
        null=True,
        blank=True
    )
    ip_address = models.GenericIPAddressField(_('IP 地址'), null=True, blank=True)

    # 时间字段
    created_at = models.DateTimeField(_('点赞时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('文章点赞')
        verbose_name_plural = _('文章点赞')
        ordering = ['-created_at']
        unique_together = [['article', 'user']]
        indexes = [
            models.Index(fields=['article', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user} - {self.article.title}'


class ArticleVersion(models.Model):
    """文章版本控制"""

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name=_('文章')
    )

    # 版本信息
    version_number = models.PositiveIntegerField(_('版本号'))
    title = models.CharField(_('标题'), max_length=500)
    content = models.TextField(_('内容'))
    description = models.TextField(_('描述'), blank=True)

    # 编辑者
    edited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('编辑者')
    )

    # 变更说明
    change_log = models.TextField(_('变更说明'), blank=True)

    # 时间字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('文章版本')
        verbose_name_plural = _('文章版本')
        ordering = ['-version_number']
        unique_together = [['article', 'version_number']]
        indexes = [
            models.Index(fields=['article', '-version_number']),
        ]

    def __str__(self):
        return f'{self.article.title} - v{self.version_number}'
