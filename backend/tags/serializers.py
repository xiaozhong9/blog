"""
标签序列化器
"""

from rest_framework import serializers
from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    """标签序列化器"""

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'slug', 'description', 'keywords',
            'articles_count', 'color', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'articles_count', 'created_at', 'updated_at')
