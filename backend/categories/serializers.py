"""
分类序列化器
"""

from rest_framework import serializers
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    """分类序列化器"""

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'description', 'icon',
            'category_type', 'keywords', 'sort_order',
            'articles_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'articles_count', 'created_at', 'updated_at')


class CategoryDetailSerializer(serializers.ModelSerializer):
    """分类详情序列化器（包含文章列表）"""

    class Meta:
        model = Category
        fields = (
            'id', 'name', 'slug', 'description', 'icon',
            'category_type', 'keywords', 'sort_order',
            'articles_count', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'articles_count', 'created_at', 'updated_at')
