"""
搜索模块 - Elasticsearch 文档定义
"""

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry

from articles.models import Article


@registry.register_document
class ArticleDocument(Document):
    """文章 Elasticsearch 文档"""

    # 字段定义
    id = fields.IntegerField()

    title = fields.TextField()
    description = fields.TextField()
    content = fields.TextField()

    slug = fields.KeywordField()

    # 作者
    author_username = fields.TextField()
    author_nickname = fields.TextField()

    # 分类
    category_name = fields.KeywordField()
    category_slug = fields.KeywordField()

    # 标签
    tags_names = fields.KeywordField(multi=True)

    # 其他字段
    locale = fields.KeywordField()
    status = fields.KeywordField()
    featured = fields.BooleanField()
    reading_time = fields.IntegerField()
    cover_image = fields.KeywordField()

    # 时间字段
    created_at = fields.DateField()
    updated_at = fields.DateField()
    published_at = fields.DateField()

    # 项目专属字段
    stars = fields.IntegerField()
    forks = fields.IntegerField()
    repo = fields.KeywordField()
    demo = fields.KeywordField()
    tech_stack = fields.KeywordField(multi=True)

    class Index:
        """索引配置"""
        name = 'articles'
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 1,
        }

    class Django:
        """Django 模型配置"""
        model = Article
        # 注意：不要在 fields 列表中包含已经显式声明的字段
        fields = []  # 所有字段都在上面显式声明了

        related_models = ['articles.Category', 'tags.Tag', 'users.User']

    def get_queryset(self):
        """自定义查询集"""
        return super().get_queryset().select_related(
            'author',
            'category'
        ).prefetch_related('tags').filter(status='published')

    def get_indexing_queryset(self):
        """索引查询集 - 避免 iterator() chunk_size 问题"""
        return self.get_queryset()

    def get_instances_from_related(self, related_instance):
        """当关联对象更新时，自动更新索引"""
        return related_instance.articles.all() if hasattr(related_instance, 'articles') else []

    # 准备方法 - 从关联对象提取数据
    def prepare_author_username(self, instance):
        """提取作者用户名"""
        return instance.author.username if instance.author else ''

    def prepare_author_nickname(self, instance):
        """提取作者昵称"""
        return instance.author.nickname if instance.author else ''

    def prepare_category_name(self, instance):
        """提取分类名称"""
        return instance.category.name if instance.category else ''

    def prepare_category_slug(self, instance):
        """提取分类 slug"""
        return instance.category.slug if instance.category else ''

    def prepare_tags_names(self, instance):
        """提取标签名称列表"""
        return [tag.name for tag in instance.tags.all()]
