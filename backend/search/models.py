"""
搜索模块 - Elasticsearch 文档定义

包含中文分词器配置和优化的字段映射
"""

from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from django.conf import settings

from articles.models import Article


@registry.register_document
class ArticleDocument(Document):
    """文章 Elasticsearch 文档

    支持中文分词、高亮显示、模糊搜索等特性
    """

    # 基础字段
    id = fields.IntegerField()

    # 使用支持中文分词的 TextField
    title = fields.TextField(
        fields={
            'keyword': fields.KeywordField(),
            'suggest': fields.TextField(),
        }
    )

    description = fields.TextField()

    content = fields.TextField()

    slug = fields.KeywordField()

    # 作者信息
    author_username = fields.KeywordField()
    author_nickname = fields.TextField()

    # 分类信息
    category_name = fields.TextField()
    category_slug = fields.KeywordField()

    # 标签（使用 KeywordField 支持精确过滤）
    tags_names = fields.KeywordField(multi=True)
    tags_slugs = fields.KeywordField(multi=True)

    # 其他字段
    locale = fields.KeywordField()
    status = fields.KeywordField()
    featured = fields.BooleanField()
    reading_time = fields.IntegerField()
    cover_image = fields.KeywordField()

    # 统计字段（用于排序）
    view_count = fields.IntegerField()
    like_count = fields.IntegerField()
    comment_count = fields.IntegerField()

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
    project_status = fields.KeywordField()

    class Index:
        """索引配置"""
        # 使用配置中的前缀
        name = f"{settings.ELASTICSEARCH_INDEX_PREFIX}articles"
        settings = {
            'number_of_shards': 1,
            'number_of_replicas': 0,  # 单节点环境设为 0
            # 高亮配置
            'highlight': {
                'max_analyzed_offset': 1000000
            }
        }

    class Django:
        """Django 模型配置"""
        model = Article
        fields = []  # 所有字段都显式声明

        related_models = ['categories.Category', 'tags.Tag', 'users.User']

    def get_queryset(self):
        """自定义查询集 - 只索引已发布的文章"""
        return super().get_queryset().select_related(
            'author',
            'category'
        ).prefetch_related('tags').filter(status='published')

    def get_indexing_queryset(self):
        """索引查询集"""
        return self.get_queryset()

    def get_instances_from_related(self, related_instance):
        """当关联对象更新时，自动更新索引"""
        if hasattr(related_instance, 'articles'):
            # 只返回已发布的文章
            return related_instance.articles.filter(status='published')
        return []

    # ============================================
    # 数据准备方法
    # ============================================

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

    def prepare_tags_slugs(self, instance):
        """提取标签 slug 列表"""
        return [tag.slug for tag in instance.tags.all()]

    def prepare_content(self, instance):
        """处理内容 - 移除 HTML 标签和代码块"""
        import re
        content = instance.content or ''

        # 移除 HTML 标签
        content = re.sub(r'<[^>]+>', ' ', content)
        # 移除代码块
        content = re.sub(r'<code[^>]*>.*?</code>', ' ', content, flags=re.DOTALL)
        content = re.sub(r'<pre[^>]*>.*?</pre>', ' ', content, flags=re.DOTALL)
        # 移除多余空白
        content = re.sub(r'\s+', ' ', content).strip()

        # 限制内容长度（ES 性能优化）
        return content[:50000] if content else ''
