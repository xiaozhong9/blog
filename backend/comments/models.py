"""
评论模型
"""

from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Comment(models.Model):
    """评论模型 (支持 Giscus 集成)"""

    class CommentStatus(models.TextChoices):
        PENDING = 'pending', _('待审核')
        APPROVED = 'approved', _('已通过')
        SPAM = 'spam', _('垃圾评论')
        DELETED = 'deleted', _('已删除')

    # 关联文章
    article = models.ForeignKey(
        'articles.Article',
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name=_('文章')
    )

    # 评论者 (可以是注册用户或访客)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='comments',
        verbose_name=_('作者')
    )

    # 访客信息 (未登录用户)
    guest_name = models.CharField(_('访客名称'), max_length=100, blank=True)
    guest_email = models.EmailField(_('访客邮箱'), blank=True)
    guest_url = models.URLField(_('访客网站'), blank=True)

    # 父评论 (支持嵌套回复)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name=_('父评论')
    )

    # 评论内容
    content = models.TextField(_('内容'))

    # Markdown 支持
    is_markdown = models.BooleanField(_('Markdown 格式'), default=True)

    # Giscus 集成字段
    giscus_id = models.CharField(_('Giscus ID'), max_length=100, blank=True)
    giscus_discussion_id = models.CharField(_('Giscus Discussion ID'), max_length=100, blank=True)

    # 状态
    status = models.CharField(
        _('状态'),
        max_length=20,
        choices=CommentStatus.choices,
        default=CommentStatus.PENDING
    )

    # IP 地址和 User Agent
    ip_address = models.GenericIPAddressField(_('IP 地址'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)

    # 点赞数
    like_count = models.PositiveIntegerField(_('点赞数'), default=0)

    # 时间字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)
    approved_at = models.DateTimeField(_('审核通过时间'), null=True, blank=True)

    class Meta:
        verbose_name = _('评论')
        verbose_name_plural = _('评论')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', '-created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['parent']),
        ]

    def __str__(self):
        name = self.author.username if self.author else self.guest_name
        return f'{name} - {self.content[:50]}'

    @property
    def display_name(self):
        """获取显示名称"""
        return self.author.username if self.author else self.guest_name

    @property
    def display_email(self):
        """获取显示邮箱"""
        return self.author.email if self.author else self.guest_email

    @property
    def is_approved(self):
        """是否已审核通过"""
        return self.status == self.CommentStatus.APPROVED

    @property
    def is_reply(self):
        """是否是回复"""
        return self.parent is not None


class CommentLike(models.Model):
    """评论点赞记录"""

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name=_('评论')
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comment_likes',
        verbose_name=_('用户')
    )

    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)

    class Meta:
        verbose_name = _('评论点赞')
        verbose_name_plural = _('评论点赞')
        unique_together = [['comment', 'user']]
        indexes = [
            models.Index(fields=['comment', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f'{self.user.username} - {self.comment.id}'
