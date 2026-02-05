# Nano Banana 后端 API 实现思路指南

> 本文档详细说明各个接口的设计思路和实现细节，便于面试时清晰讲解项目的技术亮点。

---

## 目录

1. [整体架构设计](#整体架构设计)
2. [用户认证系统](#用户认证系统)
3. [文章系统](#文章系统)
4. [评论系统](#评论系统)
5. [搜索系统](#搜索系统)
6. [统计系统](#统计系统)
7. [缓存策略](#缓存策略)
8. [异步任务](#异步任务)

---

## 整体架构设计

### 设计理念

采用 **DDD（领域驱动设计）** 思想，按业务领域划分应用模块：

```
backend/
├── users/        # 用户领域
├── articles/     # 内容领域
├── categories/   # 分类领域
├── tags/         # 标签领域
├── comments/     # 评论领域
├── search/       # 搜索领域
└── stats/        # 统计领域
```

### 统一响应格式

所有 API 端点返回统一格式，便于前端处理：

```python
# 成功响应
{
    "code": 200,
    "message": "success",
    "data": {...}
}

# 错误响应
{
    "code": 400,
    "message": "错误描述",
    "data": null
}
```

**实现位置**：在 `config/exceptions.py` 中通过 `custom_exception_handler` 统一处理异常。

---

## 用户认证系统

### JWT 认证架构

**技术选型**：使用 `djangorestframework-simplejwt` 实现 JWT 认证。

**配置要点** ([config/settings/base.py:223-236](../backend/config/settings/base.py#L223-L236))：

```python
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),   # 访问令牌 1 小时
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),      # 刷新令牌 7 天
    'ROTATE_REFRESH_TOKENS': True,                     # 刷新时轮换 Refresh Token
    'BLACKLIST_AFTER_ROTATION': True,                  # 轮换后旧 Token 加入黑名单
    'UPDATE_LAST_LOGIN': True,                         # 更新最后登录时间
}
```

**面试亮点**：
- **Token 轮换机制**：每次刷新 Token 后，旧的 Refresh Token 会被加入黑名单，防止 Token 被盗用后持续使用
- **自动刷新**：前端在 401 错误时自动调用刷新接口，无感续期

### 自定义用户模型

**设计** ([users/models.py](../backend/users/models.py))：

```python
class User(AbstractUser):
    role = models.CharField(choices=['admin', 'editor', 'user'], default='user')
    email = models.EmailField(unique=True, null=True)
    nickname = models.CharField(max_length=100, blank=True)
    avatar = models.URLField(blank=True)
    bio = models.TextField(blank=True)

    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_editor(self):
        return self.role in [self.Role.ADMIN, self.Role.EDITOR]
```

**面试亮点**：
- 继承 `AbstractUser` 保留 Django 原有认证功能
- 扩展角色字段实现基于角色的权限控制（RBAC）
- 使用 `AUTH_USER_MODEL` 配置让 Django 使用自定义模型

---

## 文章系统

### 核心模型设计

**Article 模型** ([articles/models.py](../backend/articles/models.py))：

```python
class Article(models.Model):
    class ArticleStatus(models.TextChoices):
        DRAFT = 'draft'
        PUBLISHED = 'published'
        ARCHIVED = 'archived'

    title = models.CharField(max_length=500)
    slug = models.SlugField(max_length=200, unique=True)
    content = models.TextField(blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey('categories.Category', on_delete=models.SET_NULL, null=True)
    tags = models.ManyToManyField('tags.Tag', blank=True)
    status = models.CharField(choices=ArticleStatus.choices, default='draft')
    featured = models.BooleanField(default=False)
    view_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
```

### 智能 slug 生成与阅读时间计算

**实现** ([articles/models.py:123-134](../backend/articles/models.py#L123-L134))：

```python
def save(self, *args, **kwargs):
    # 自动生成 slug
    if not self.slug and self.title:
        self.slug = slugify(self.title)

    # 自动计算阅读时间（假设每分钟阅读 200 字）
    if self.content and not self.reading_time:
        word_count = len(self.content)
        self.reading_time = max(1, word_count // 200)

    super().save(*args, **kwargs)
```

**面试亮点**：
- **自动化**：在模型 `save` 方法中处理，无需手动调用
- **阅读时间算法**：中文按字数计算（200 字/分钟），提升用户体验

### 双模式点赞系统

**设计思路**：支持登录用户和匿名用户两种点赞方式。

**实现** ([articles/views.py:331-373](../backend/articles/views.py#L331-L373))：

```python
@action(detail=True, methods=['post'])
def like(self, request, pk=None):
    article = self.get_object()

    if request.user.is_authenticated:
        # 登录用户：检查 user + article 组合
        like_exists = article.likes.filter(user=request.user).exists()
        if like_exists:
            return Response({'code': 400, 'message': '已经点赞过了'})

        ArticleLike.objects.create(article=article, user=request.user)
    else:
        # 匿名用户：基于 IP 地址
        ip_address = self.get_client_ip(request)
        like_exists = article.likes.filter(ip_address=ip_address).exists()
        if like_exists:
            return Response({'code': 400, 'message': '已经点赞过了'})

        ArticleLike.objects.create(article=article, ip_address=ip_address)

    # 使用 F() 表达式原子性更新点赞数（避免竞态条件）
    Article.objects.filter(pk=article.pk).update(like_count=F('like_count') + 1)
```

**面试亮点**：
- **F() 表达式**：在数据库层面原子性更新计数器，避免竞态条件
- **IP 去重**：匿名用户通过 IP 地址防止重复点赞
- **兼容性**：同时支持登录和未登录用户

### 相关文章推荐算法

**实现** ([articles/views.py:428-470](../backend/articles/views.py#L428-L470))：

```python
@action(detail=True, methods=['get'])
def related(self, request, pk=None):
    article = self.get_object()
    article_tags = article.tags.all()

    if not article_tags:
        # 无标签：返回同分类文章
        related = Article.objects.filter(
            category=article.category,
            status='published'
        ).exclude(pk=article.pk)[:4]
    else:
        # 基于标签相似度计算
        related_articles = []
        for related_article in Article.objects.filter(status='published').exclude(pk=article.pk):
            common_tags = set(article_tags).intersection(set(related_article.tags.all()))
            similarity = len(common_tags)

            if similarity > 0:
                related_articles.append({'article': related_article, 'similarity': similarity})

        # 按相似度排序
        related_articles.sort(key=lambda x: x['similarity'], reverse=True)
        related = [item['article'] for item in related_articles[:4]]
```

**面试亮点**：
- **两级推荐策略**：有标签用标签相似度，无标签用同分类
- **相似度计算**：基于共同标签数量排序，推荐更精准的内容

### 文章版本控制

**实现** ([articles/models.py:216-256](../backend/articles/models.py#L216-L256))：

```python
class ArticleVersion(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=500)
    content = models.TextField()
    edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    change_log = models.TextField(blank=True)  # 变更说明

    class Meta:
        unique_together = [['article', 'version_number']]
```

**面试亮点**：
- **完整历史记录**：保留每次修改的内容和编辑者
- **变更日志**：`change_log` 字段记录修改原因
- **版本号自增**：通过查询最新版本号 +1 实现

### 图片上传接口

**实现** ([articles/views.py:487-589](../backend/articles/views.py#L487-L589))：

```python
@csrf_exempt
def image_upload_view(request):
    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        return JsonResponse({'code': 400, 'message': f'不支持的文件类型'})

    # 验证文件大小（10MB）
    max_size = 10 * 1024 * 1024
    if file.size > max_size:
        return JsonResponse({'code': 400, 'message': '文件过大'})

    # 按分类和日期组织目录
    date_path = datetime.now().strftime('%Y/%m/%d')
    file_path = os.path.join(f'uploads/images/{safe_category}', date_path, unique_filename)

    # 保存文件
    save_path = default_storage.save(file_path, file)
    full_url = f"{settings.SITE_URL}{default_storage.url(save_path)}"

    return JsonResponse({'code': 200, 'data': {'url': full_url}})
```

**面试亮点**：
- **目录组织**：按分类和日期分层存储，便于管理和备份
- **UUID 命名**：避免文件名冲突和中文路径问题
- **安全验证**：类型和大小双重验证

---

## 评论系统

### 嵌套回复设计

**模型** ([comments/models.py:43-50](../backend/comments/models.py#L43-L50))：

```python
class Comment(models.Model):
    article = models.ForeignKey('articles.Article', on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField()
    status = models.CharField(choices=[...], default='pending')
```

**面试亮点**：
- **自关联外键**：`parent` 指向自身实现树形结构
- **related_name='replies'**：通过 `comment.replies.all()` 获取所有子评论

### 访客评论支持

**设计** ([comments/models.py:38-40](../backend/comments/models.py#L38-L40))：

```python
# 访客信息（未登录用户）
guest_name = models.CharField(max_length=100, blank=True)
guest_email = models.EmailField(blank=True)
guest_url = models.URLField(blank=True)
```

**面试亮点**：
- **灵活认证**：支持注册用户和访客两种评论方式
- **数据模型兼容**：通过 `display_name` 和 `display_email` 属性统一获取

### 评论审核机制

**状态流程** ([comments/models.py:13-17](../backend/comments/models.py#L13-L17))：

```python
class CommentStatus(models.TextChoices):
    PENDING = 'pending'      # 待审核
    APPROVED = 'approved'    # 已通过
    SPAM = 'spam'           # 垃圾评论
    DELETED = 'deleted'     # 已删除
```

**API 实现** ([comments/views.py:252-298](../backend/comments/views.py#L252-L298))：

```python
@action(detail=True, methods=['post'])
def approve(self, request, pk=None):
    if not request.user.is_staff:
        return Response({'code': 403, 'message': '权限不足'})

    comment = self.get_object()
    comment.status = 'approved'
    comment.approved_at = timezone.now()
    comment.save()
```

**面试亮点**：
- **权限控制**：只有管理员可以审核
- **审核时间戳**：记录审核通过时间，便于数据分析

### Giscus 集成字段

**设计** ([comments/models.py:58-60](../backend/comments/models.py#L58-L60))：

```python
giscus_id = models.CharField(max_length=100, blank=True)
giscus_discussion_id = models.CharField(max_length=100, blank=True)
```

**面试亮点**：
- **双轨评论**：同时支持传统评论和 GitHub Discussions 评论
- **数据同步**：通过 ID 字段关联两种评论系统

---

## 搜索系统

### Elasticsearch 文档设计

**文档模型** ([search/models.py:12-86](../backend/search/models.py#L12-L86))：

```python
@registry.register_document
class ArticleDocument(Document):
    title = fields.TextField()
    description = fields.TextField()
    content = fields.TextField()

    # 关联字段
    author_username = fields.TextField()
    category_name = fields.KeywordField()
    tags_names = fields.KeywordField(multi=True)

    class Index:
        name = 'articles'
        settings = {'number_of_shards': 1, 'number_of_replicas': 1}

    def prepare_author_username(self, instance):
        return instance.author.username if instance.author else ''
```

**面试亮点**：
- **字段分离**：关联对象字段通过 `prepare_*` 方法预处理，避免嵌套查询
- **索引配置**：单分片适合中小规模博客

### 多字段加权搜索

**实现** ([search/views.py:82-88](../backend/search/views.py#L82-L88))：

```python
q = Q(
    'multi_match',
    query=query,
    fields=['title^3', 'description^2', 'content'],  # 权重：标题 3x，描述 2x
    fuzziness='AUTO'                                  # 模糊匹配
)
```

**面试亮点**：
- **字段权重**：标题匹配权重最高，提升搜索准确性
- **模糊匹配**：`fuzziness='AUTO'` 自动处理拼写错误

### 搜索高亮

**实现** ([search/views.py:105-113](../backend/search/views.py#L105-L113))：

```python
search = search.highlight(
    'title',
    'description',
    'content',
    fragment_size=150,       # 片段长度
    number_of_fragments=3,   # 返回片段数
    pre_tags=['<em>'],       # 高亮前缀
    post_tags=['</em>']      # 高亮后缀
)
```

### 搜索建议（自动补全）

**实现** ([search/views.py:218-221](../backend/search/views.py#L218-L221))：

```python
# 使用 match_phrase_prefix 查询实现前缀匹配
search = ArticleDocument.search()
search = search.query('match_phrase_prefix', title=query)
search = search[:10]
```

**面试亮点**：
- **match_phrase_prefix**：专门用于前缀匹配的查询类型
- **性能优化**：限制返回 10 条结果

---

## 统计系统

### 热度分数算法

**公式** ([stats/models.py:93-104](../backend/stats/models.py#L93-L104))：

```python
def calculate_hot_score(self):
    """
    热度分数 = 阅读量 × 1 + 点赞数 × 5 + 评论数 × 10 + 分享数 × 20
    """
    self.hot_score = (
        self.view_count * 1 +
        self.like_count * 5 +
        self.comment_count * 10 +
        self.share_count * 20
    )
```

**面试亮点**：
- **权重设计**：互动深度越高权重越大（阅读 < 点赞 < 评论 < 分享）
- **动态排序**：热度分数实时更新，反映当前热门内容

### 热门文章缓存

**设计** ([stats/models.py:107-143](../backend/stats/models.py#L107-L143))：

```python
class PopularArticles(models.Model):
    period = models.CharField choices=[...], unique=True)
    article_ids = models.JSONField(default=list)  # 存储 ID 列表
    cached_at = models.DateTimeField(auto_now=True)

    def is_expired(self, hours=1):
        """检查缓存是否过期"""
        expiry_time = timezone.now() - timedelta(hours=hours)
        return self.cached_at < expiry_time
```

**面试亮点**：
- **JSON 字段**：存储 ID 列表而非完整对象，节省空间
- **多周期缓存**：每日/每周/每月/全部时间独立缓存
- **过期检测**：`is_expired()` 方法判断是否需要更新

### 用户行为追踪

**模型** ([stats/models.py:207-275](../backend/stats/models.py#L207-L275))：

```python
class UserAction(models.Model):
    class ActionType(models.TextChoices):
        VIEW_ARTICLE = 'view_article'
        LIKE_ARTICLE = 'like_article'
        COMMENT = 'comment'
        SEARCH = 'search'

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(choices=ActionType.choices)
    article = models.ForeignKey(Article, on_delete=models.SET_NULL, null=True)
    metadata = models.JSONField(blank=True, null=True)  # 存储额外信息
```

**面试亮点**：
- **完整追踪**：记录用户所有行为，便于用户画像分析
- **灵活元数据**：JSON 字段存储不同行为的额外信息

---

## 缓存策略

### Redis 缓存配置

**设置** ([config/settings/base.py:120-134](../backend/config/settings/base.py#L120-L134))：

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 100}
        },
        'KEY_PREFIX': 'banana_cache',
    }
}

# 会话存储在 Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

**面试亮点**：
- **连接池**：最大 100 连接，避免频繁创建连接
- **Key 前缀**：避免多项目共享 Redis 时键冲突
- **会话缓存**：用户会话存储在 Redis，支持分布式部署

---

## 异步任务

### Celery 定时任务配置

**调度器** ([config/celery.py:20-37](../backend/config/celery.py#L20-L37))：

```python
app.conf.beat_schedule = {
    # 每日生成统计数据
    'generate-daily-stats': {
        'task': 'stats.tasks.generate_daily_statistics',
        'schedule': crontab(hour=0, minute=0),  # 每天 00:00
    },
    # 每小时清理过期缓存
    'clean-expired-cache': {
        'task': 'articles.tasks.clean_expired_cache',
        'schedule': crontab(minute=0),  # 每小时
    },
    # 每 15 分钟同步热门文章缓存
    'sync-popular-articles': {
        'task': 'stats.tasks.sync_popular_articles_cache',
        'schedule': crontab(minute='*/15'),  # 每 15 分钟
    },
}
```

**面试亮点**：
- **任务分级**：高频（15 分钟）、中频（小时）、低频（日）任务
- **解耦设计**：异步任务不阻塞主线程，提升 API 响应速度

---

## 性能优化技巧

### 数据库查询优化

**select_related 和 prefetch_related** ([articles/views.py:29](../backend/articles/views.py#L29))：

```python
queryset = Article.objects.select_related('author', 'category').prefetch_related('tags')
```

**面试亮点**：
- **select_related**：处理 ForeignKey（一对一、多对一），使用 SQL JOIN 减少查询次数
- **prefetch_related**：处理 ManyToMany（一对多、多对多），使用 Python 内存关联

### 数据库索引设计

**Article 模型索引** ([articles/models.py:111-118](../backend/articles/models.py#L111-L118))：

```python
class Meta:
    indexes = [
        models.Index(fields=['slug']),           # URL 查找
        models.Index(fields=['status']),          # 状态过滤
        models.Index(fields=['featured']),        # 精选文章
        models.Index(fields=['locale']),          # 语言过滤
        models.Index(fields=['-published_at']),   # 时间排序（降序）
        models.Index(fields=['-view_count']),     # 热度排序（降序）
    ]
```

**面试亮点**：
- **复合索引**：常用查询条件组合索引
- **降序索引**：`-published_at` 支持时间倒序查询

---

## API 端点总览

| 模块 | 端点 | 方法 | 说明 |
|------|------|------|------|
| 用户 | `/api/auth/register/` | POST | 用户注册 |
| 用户 | `/api/auth/login/` | POST | 登录获取 Token |
| 用户 | `/api/auth/refresh/` | POST | 刷新 Token |
| 文章 | `/api/articles/` | GET | 文章列表（支持过滤、分页） |
| 文章 | `/api/articles/{id}/` | GET | 文章详情（自动增加阅读量） |
| 文章 | `/api/articles/{id}/like/` | POST | 点赞文章 |
| 文章 | `/api/articles/{id}/related/` | GET | 相关文章推荐 |
| 文章 | `/api/articles/featured/` | GET | 精选文章 |
| 文章 | `/api/upload/image/` | POST | 图片上传 |
| 评论 | `/api/comments/` | GET/POST | 评论列表/创建 |
| 评论 | `/api/comments/{id}/approve/` | POST | 审核通过（管理员） |
| 搜索 | `/api/search/?q=关键词` | GET | 全文搜索 |
| 搜索 | `/api/search/suggest/?q=前缀` | GET | 搜索建议 |
| 统计 | `/api/stats/overview/` | GET | 总览统计 |
| 统计 | `/api/stats/popular-articles/` | GET | 热门文章 |

---

## 面试话术建议

### 介绍项目架构

> "这个项目采用 Django REST Framework 构建后端 API，按业务领域划分为 7 个应用模块。整体采用统一的响应格式，使用 JWT 进行无状态认证，并通过 Redis 缓存和 Celery 异步任务提升性能。"

### 讲技术难点

> "最有趣的是实现了一个双模式点赞系统：登录用户通过用户 ID 去重，匿名用户通过 IP 地址去重。在更新计数器时使用了 Django 的 F() 表达式在数据库层面原子性更新，避免了并发条件下的竞态问题。"

### 讲搜索优化

> "搜索方面使用 Elasticsearch 实现了多字段加权搜索，标题匹配的权重是内容的 3 倍。同时实现了高亮显示和搜索建议功能，提升用户体验。文档设计上通过 prepare_* 方法预处理关联字段，避免索引时的嵌套查询。"

### 讲性能优化

> "性能方面主要做了三点：一是使用 select_related 和 prefetch_related 优化数据库查询，减少 N+1 问题；二是为常用查询字段建立索引，包括降序索引支持时间倒序；三是使用 Redis 缓存热门文章和用户会话，减少数据库压力。"
