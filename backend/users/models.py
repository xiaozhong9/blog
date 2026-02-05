"""
用户模型
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """自定义用户管理器"""

    def create_user(self, username, email=None, password=None, **extra_fields):
        """创建普通用户"""
        if not username:
            raise ValueError(_('用户必须提供用户名'))

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('超级用户必须设置 is_staff=True'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('超级用户必须设置 is_superuser=True'))

        return self.create_user(username, email, password, **extra_fields)


class User(AbstractUser):
    """自定义用户模型"""

    class Role(models.TextChoices):
        ADMIN = 'admin', _('管理员')
        EDITOR = 'editor', _('编辑')
        USER = 'user', _('用户')

    # 扩展字段
    email = models.EmailField(_('邮箱'), unique=True, null=True, blank=True)
    nickname = models.CharField(_('昵称'), max_length=100, blank=True)
    avatar = models.URLField(_('头像 URL'), blank=True)
    bio = models.TextField(_('个人简介'), blank=True)
    website = models.URLField(_('个人网站'), blank=True)

    # 社交链接
    github_url = models.URLField(_('GitHub'), blank=True, help_text=_('GitHub 个人主页'))
    twitter_url = models.URLField(_('Twitter'), blank=True, help_text=_('Twitter 个人主页'))
    linkedin_url = models.URLField(_('LinkedIn'), blank=True, help_text=_('LinkedIn 个人主页'))

    # 技能和时间线（JSON 字段）
    skills = models.JSONField(_('技能'), default=dict, blank=True, help_text=_('技能栈数据'))
    timeline = models.JSONField(_('时间线'), default=list, blank=True, help_text=_('个人经历时间线'))

    # 我的故事
    story = models.TextField(_('我的故事'), blank=True, help_text=_('个人经历故事，支持 Markdown'))

    # 用户角色
    role = models.CharField(
        _('角色'),
        max_length=20,
        choices=Role.choices,
        default=Role.USER
    )

    # 状态字段
    is_verified = models.BooleanField(_('邮箱已验证'), default=False)

    # 统计字段
    articles_count = models.PositiveIntegerField(_('文章数量'), default=0)
    comments_count = models.PositiveIntegerField(_('评论数量'), default=0)

    # 时间字段
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    # 配置
    objects = UserManager()

    class Meta:
        verbose_name = _('用户')
        verbose_name_plural = _('用户')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['role']),
        ]

    def __str__(self):
        return self.username or self.email

    @property
    def full_name(self):
        """获取全名"""
        return self.nickname or self.username

    def is_admin(self):
        """是否是管理员"""
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_editor(self):
        """是否是编辑"""
        return self.role in [self.Role.ADMIN, self.Role.EDITOR]
