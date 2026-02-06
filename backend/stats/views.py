"""
统计视图
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny
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
    """统计视图集 - 允许匿名访问"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='获取总览统计',
        operation_description='获取网站的总体统计数据',
        responses={200: OverviewSerializer}
    )
    @action(detail=False, methods=['get'])
    def overview(self, request):
        """总览统计"""
        # 获取当前日期
        today = timezone.now().date()
        today_start = timezone.make_aware(timezone.datetime(today.year, today.month, today.day))

        # 使用单次聚合查询获取文章统计
        article_stats = Article.objects.aggregate(
            total_articles=Count('id', filter=Q(status='published')),
            articles_draft=Count('id', filter=Q(status='draft')),
            total_views=Sum('view_count'),
            today_articles=Count('id', filter=Q(status='published', created_at__gte=today_start))
        )
        total_articles = article_stats['total_articles'] or 0
        articles_draft = article_stats['articles_draft'] or 0
        total_views = article_stats['total_views'] or 0
        today_articles = article_stats['today_articles'] or 0

        # 用户和评论统计
        total_users = User.objects.count()
        today_users = User.objects.filter(created_at__gte=today_start).count()
        total_comments = Comment.objects.filter(status='approved').count()
        today_comments = Comment.objects.filter(created_at__gte=today_start).count()

        # 按分类统计（单次查询）
        category_stats = dict(
            Article.objects.filter(status='published')
            .values('category__category_type')
            .annotate(count=Count('id'))
            .values_list('category__category_type', 'count')
        )
        # 确保所有分类都有值
        for category_type in ['blog', 'projects', 'life', 'notes']:
            category_stats.setdefault(category_type, 0)

        # 热门分类和标签（使用 select_related/prefetch_related 优化）
        popular_categories = list(
            Category.objects
            .filter(articles__status='published')
            .annotate(article_count=Count('articles'))
            .order_by('-article_count')[:5]
            .values('slug', 'name', 'article_count')
        )

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

            'articles_published': total_articles,
            'articles_draft': articles_draft,

            'today_articles': today_articles,
            'today_users': today_users,
            'today_comments': today_comments,
            'today_views': 0,  # 需要从 ArticleView 表查询

            'category_stats': category_stats,
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
        from articles.serializers import ArticleListSerializer

        # 获取查询参数
        period = request.query_params.get('period', 'all')  # all, week, month
        limit = int(request.query_params.get('limit', 10))

        # 构建查询
        queryset = Article.objects.filter(status='published')

        # 根据时间范围过滤
        if period == 'week':
            week_ago = timezone.now() - timedelta(days=7)
            queryset = queryset.filter(created_at__gte=week_ago)
        elif period == 'month':
            month_ago = timezone.now() - timedelta(days=30)
            queryset = queryset.filter(created_at__gte=month_ago)

        # 排序并限制数量
        queryset = queryset.select_related('author', 'category').prefetch_related('tags')
        queryset = queryset.order_by('-view_count')[:limit]

        serializer = ArticleListSerializer(queryset, many=True)

        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })
