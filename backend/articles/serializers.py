"""
文章序列化器
"""

from rest_framework import serializers
from .models import Article, ArticleView, ArticleVersion
from categories.models import Category
from tags.models import Tag


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器（简化版）"""

    class Meta:
        model = Category
        fields = ('id', 'slug', 'name', 'category_type', 'icon', 'description')


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器（简化版）"""

    class Meta:
        model = Tag
        fields = ('id', 'slug', 'name', 'color')


class AuthorSerializer(serializers.Serializer):
    """作者序列化器（简化版）"""
    id = serializers.IntegerField()
    username = serializers.CharField()
    nickname = serializers.CharField()
    avatar = serializers.CharField()


class ArticleListSerializer(serializers.ModelSerializer):
    """文章列表序列化器"""

    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category_type = serializers.CharField(read_only=True)

    class Meta:
        model = Article
        fields = (
            'id', 'slug', 'title', 'description', 'cover_image',
            'author', 'category', 'category_type', 'tags', 'locale', 'reading_time',
            'status', 'featured', 'view_count', 'like_count', 'comment_count',
            'stars', 'forks', 'repo', 'demo', 'tech_stack', 'project_status',
            'created_at', 'updated_at', 'published_at'
        )


class ArticleDetailSerializer(serializers.ModelSerializer):
    """文章详情序列化器"""

    author = AuthorSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    category_type = serializers.CharField(read_only=True)

    class Meta:
        model = Article
        fields = (
            'id', 'slug', 'title', 'description', 'content',
            'author', 'category', 'category_type', 'tags',
            'locale', 'reading_time', 'status', 'featured',
            'cover_image', 'keywords', 'view_count', 'like_count',
            'comment_count', 'stars', 'forks', 'repo', 'demo',
            'tech_stack', 'project_status', 'created_at',
            'updated_at', 'published_at'
        )
        read_only_fields = ('id', 'slug', 'view_count', 'like_count',
                           'comment_count', 'created_at', 'updated_at')


class ArticleCreateUpdateSerializer(serializers.ModelSerializer):
    """文章创建/更新序列化器"""

    category_id = serializers.IntegerField(
        required=False,
        write_only=True
    )
    tag_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    slug = serializers.SlugField(required=False, allow_blank=True)  # 允许为空，自动生成

    class Meta:
        model = Article
        fields = (
            'title', 'slug', 'description', 'content',
            'category_id', 'tag_ids', 'locale', 'reading_time',
            'status', 'featured', 'cover_image', 'keywords',
            'stars', 'forks', 'repo', 'demo', 'tech_stack',
            'project_status', 'published_at'
        )
        # 更新时，所有字段都变为可选（除了在 create 方法中会处理）
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'content': {'required': False},
            'locale': {'required': False},
            'reading_time': {'required': False},
            'status': {'required': False},
            'featured': {'required': False},
            'cover_image': {'required': False},
            'keywords': {'required': False},
            'published_at': {'required': False},
        }

    def create(self, validated_data):
        """创建文章"""
        tag_ids = validated_data.pop('tag_ids', [])
        category_id = validated_data.pop('category_id', None)

        # 处理 category
        if category_id:
            from categories.models import Category
            try:
                category = Category.objects.get(id=category_id)
                validated_data['category'] = category
            except Category.DoesNotExist:
                raise serializers.ValidationError({'category_id': '分类不存在'})

        # 处理 tags
        tags = Tag.objects.filter(id__in=tag_ids) if tag_ids else []

        # 如果没有提供 slug，从标题自动生成
        from django.utils.text import slugify
        if not validated_data.get('slug'):
            base_slug = slugify(validated_data['title'])
            slug = base_slug
            counter = 1
            # 确保 slug 唯一
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            validated_data['slug'] = slug

        article = Article.objects.create(**validated_data)
        article.tags.set(tags)

        # 如果是发布状态，记录发布时间
        if article.status == Article.ArticleStatus.PUBLISHED and not article.published_at:
            from django.utils import timezone
            article.published_at = timezone.now()
            article.save()

        return article

    def update(self, instance, validated_data):
        """更新文章"""
        tag_ids = validated_data.pop('tag_ids', None)
        category_id = validated_data.pop('category_id', None)

        # 处理 category
        if category_id is not None:
            from categories.models import Category
            try:
                category = Category.objects.get(id=category_id)
                validated_data['category'] = category
            except Category.DoesNotExist:
                raise serializers.ValidationError({'category_id': '分类不存在'})

        # 更新字段
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        # 更新标签
        if tag_ids is not None:
            # 获取或创建标签
            tags = []
            for tag_id in tag_ids:
                try:
                    tag = Tag.objects.get(id=tag_id)
                    tags.append(tag)
                except Tag.DoesNotExist:
                    pass
            instance.tags.set(tags)

        return instance


class ArticleVersionSerializer(serializers.ModelSerializer):
    """文章版本序列化器"""

    edited_by = AuthorSerializer(read_only=True)

    class Meta:
        model = ArticleVersion
        fields = (
            'id', 'version_number', 'title', 'content',
            'description', 'edited_by', 'change_log', 'created_at'
        )
        read_only_fields = ('id', 'version_number', 'created_at')
