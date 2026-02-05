"""
统计视图
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from drf_yasg.utils import swagger_auto_schema
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta

from articles.models import Article
from users.models import User
from comments.models import Comment
from categories.models import Category
from tags.models import Tag
from .serializers import OverviewSerializer


class StatsViewSet(ViewSet):
    """统计视图集"""

    @swagger_auto_schema(
        operation_summary='获取总览统计',
        operation_description='获取网站的总体统计数据',
        responses={200: OverviewSerializer}
    )
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """总览统计"""
        # 获取当前日期和时间
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)

        # 总体统计
        total_articles = Article.objects.filter(status='published').count()
        total_users = User.objects.count()
        total_comments = Comment.objects.filter(status='approved').count()
        total_views = Article.objects.aggregate(total=Sum('view_count'))['total'] or 0

        # 文章统计
        articles_published = Article.objects.filter(status='published').count()
        articles_draft = Article.objects.filter(status='draft').count()

        # 按分类统计（文章/项目/生活）
        category_stats = {}
        for category_type in ['blog', 'projects', 'life', 'notes']:
            category_stats[category_type] = Article.objects.filter(
                status='published',
                category__category_type=category_type
            ).count()

        # 今日统计
        today_articles = Article.objects.filter(created_at__date=today).count()
        today_users = User.objects.filter(created_at__date=today).count()
        today_comments = Comment.objects.filter(created_at__date=today).count()
        today_views = 0  # 需要从 ArticleView 表查询

        # 热门分类（按文章数量）
        popular_categories = list(
            Category.objects
            .filter(articles__status='published')
            .annotate(article_count=Count('articles'))
            .order_by('-article_count')[:5]
            .values('slug', 'name', 'article_count')
        )

        # 热门标签（按文章数量）
        popular_tags = list(
            Tag.objects
            .annotate(article_count=Count('articles'))
            .order_by('-article_count')[:10]
            .values('slug', 'name', 'color', 'article_count')
        )

        data = {
            'total_articles': total_articles,
            'total_users': total_users,
            'total_comments': total_comments,
            'total_views': total_views,

            'articles_published': articles_published,
            'articles_draft': articles_draft,

            'today_articles': today_articles,
            'today_users': today_users,
            'today_comments': today_comments,
            'today_views': today_views,

            'category_stats': category_stats,  # 新增：按分类统计
            'popular_categories': popular_categories,
            'popular_tags': popular_tags
        }

        return Response({
            'code': 200,
            'message': 'success',
            'data': data
        })

    @swagger_auto_schema(
        operation_summary='获取热门文章',
        operation_description='按阅读量排序获取热门文章',
        responses={200: '文章列表'}
    )
    @action(detail=False, methods=['get'])
    def popular_articles(self, request):
        """热门文章"""
        # 获取查询参数
        period = request.query_params.get('period', 'all')  # all, week, month
        limit = int(request.query_params.get('limit', 10))

        # 根据时间范围过滤
        queryset = Article.objects.filter(status='published')
        date_filter = Q()

        if period == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            date_filter &= Q(created_at__gte=week_ago)
        elif period == 'month':
            month_ago = timezone.now() - timedelta(days=30)
            date_filter &= Q(created_at__gte=month_ago)

        queryset = queryset.filter(date_filter).order_by('-view_count')[:limit]

        # 序列化数据
        articles_data = []
        for article in queryset:
            articles_data.append({
                'id': article.id,
                'slug': article.slug,
                'title': article.title,
                'description': article.description,
                'cover_image': article.cover_image,
                'view_count': article.view_count,
                'like_count': article.like_count,
                'comment_count': article.comment_count,
                'created_at': article.created_at,
                'author': {
                    'id': article.author.id,
                    'username': article.author.username,
                    'nickname': article.author.nickname
                } if article.author else None,
                'category': {
                    'slug': article.category.slug,
                    'name': article.category.name
                } if article.category else None
            })

        return Response({
            'code': 200,
            'message': 'success',
            'data': articles_data
        })
