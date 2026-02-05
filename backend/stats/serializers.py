"""
统计序列化器
"""

from rest_framework import serializers
from .models import DailyStats, ArticleStats, PopularArticles


class DailyStatsSerializer(serializers.ModelSerializer):
    """每日统计序列化器"""

    class Meta:
        model = DailyStats
        fields = (
            'date', 'articles_published', 'articles_draft', 'articles_created',
            'users_new', 'users_total', 'comments_new', 'comments_total',
            'views_total', 'views_unique', 'likes_total'
        )


class ArticleStatsSerializer(serializers.ModelSerializer):
    """文章统计序列化器"""
    article_title = serializers.CharField(source='article.title', read_only=True)
    article_slug = serializers.CharField(source='article.slug', read_only=True)

    class Meta:
        model = ArticleStats
        fields = (
            'article', 'article_title', 'article_slug', 'view_count',
            'view_count_unique', 'like_count', 'comment_count',
            'share_count', 'bookmark_count', 'hot_score'
        )


class OverviewSerializer(serializers.Serializer):
    """总览统计序列化器"""

    total_articles = serializers.IntegerField()
    total_users = serializers.IntegerField()
    total_comments = serializers.IntegerField()
    total_views = serializers.IntegerField()

    articles_published = serializers.IntegerField()
    articles_draft = serializers.IntegerField()

    today_articles = serializers.IntegerField()
    today_users = serializers.IntegerField()
    today_comments = serializers.IntegerField()
    today_views = serializers.IntegerField()

    popular_categories = serializers.ListField()
    popular_tags = serializers.ListField()


class PopularArticlesSerializer(serializers.ModelSerializer):
    """热门文章序列化器"""

    class Meta:
        model = PopularArticles
        fields = ('period', 'article_ids', 'cached_at')
