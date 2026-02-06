"""
文章视图
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils import timezone
from django.db.models import Q, F, Count
from django.core.cache import cache
from utils import get_client_ip
from utils.cache_utils import (
    CacheKeyBuilder,
    get_or_set,
    get_many,
    set_many,
    CacheWarmer,
    RateLimiter
)

from .models import Article, ArticleVersion
from .serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer,
    ArticleCreateUpdateSerializer,
    ArticleVersionSerializer
)


class ArticleViewSet(ModelViewSet):
    """文章视图集"""

    queryset = Article.objects.select_related('author', 'category').prefetch_related('tags')

    def get_object(self):
        """
        重写 get_object 方法支持 slug 和 ID 查找
        使用 self.queryset 以利用 select_related/prefetch_related
        """
        lookup_value = self.kwargs.get(self.lookup_field)
        queryset = self.get_queryset()

        # 尝试 slug 查询
        try:
            return queryset.get(slug=lookup_value)
        except Article.DoesNotExist:
            pass

        # 尝试 ID 查询
        if lookup_value.isdigit():
            try:
                return queryset.get(pk=int(lookup_value))
            except Article.DoesNotExist:
                pass

        from django.http import Http404
        raise Http404('文章不存在')

    # 根据操作选择不同的序列化器
    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        elif self.action in ['retrieve', 'featured', 'popular']:
            return ArticleDetailSerializer
        return ArticleCreateUpdateSerializer

    def get_permissions(self):
        """权限控制"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        elif self.action in ['create_version']:
            return [IsAuthenticated()]
        return []

    def get_queryset(self):
        """自定义查询集"""
        queryset = super().get_queryset()
        params = self.request.query_params

        # 只显示已发布的文章（非管理员）
        user = self.request.user
        if not user.is_authenticated or not user.is_staff:
            queryset = queryset.filter(status='published')

        # 按分类过滤（支持 category_type 如 'blog', 'projects'）
        category_param = params.get('category')
        if category_param:
            queryset = queryset.filter(category__category_type=category_param)

        # 按标签过滤
        tag_slug = params.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)

        # 按语言过滤
        locale = params.get('locale')
        if locale:
            queryset = queryset.filter(locale=locale)

        # 按状态过滤
        status_param = params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        # 按作者过滤
        author_id = params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        # 搜索
        search = params.get('search')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(content__icontains=search)
            )

        return queryset.distinct()

    @swagger_auto_schema(
        operation_summary='获取文章列表',
        operation_description='支持分页、过滤、排序和搜索。使用 Elasticsearch 查询 + MySQL 统计数据',
        responses={200: ArticleListSerializer}
    )
    def list(self, request, *args, **kwargs):
        """文章列表 - 从 ES 查询 + MySQL 批量查询统计"""
        from search.models import ArticleDocument

        params = request.query_params

        # 1. 从 ES 构建搜索查询
        search = ArticleDocument.search()

        # 权限过滤
        user = request.user
        if not user.is_authenticated or not user.is_staff:
            search = search.filter('term', status='published')

        # 按分类过滤（支持 category_type 如 'blog', 'projects'）
        category_param = params.get('category')
        if category_param:
            # 使用 category_type 而不是 category_slug
            # 因为 ES 中存储的是 category_slug（如 'tech-blog'），但前端传递的是 category_type（如 'blog'）
            # 需要查询 MySQL 获取对应的 slug
            from categories.models import Category
            try:
                category = Category.objects.get(category_type=category_param)
                search = search.filter('term', category_slug=category.slug)
            except Category.DoesNotExist:
                # 如果分类不存在，返回空结果
                search = search.filter('term', id=-1)

        # 按标签过滤（支持多个标签，逗号分隔）
        tags = params.get('tags')
        if tags:
            tag_list = tags.split(',')
            search = search.filter('terms', tags_names=tag_list)

        # 按语言过滤
        locale = params.get('locale')
        if locale:
            search = search.filter('term', locale=locale)

        # 按状态过滤（管理员）
        status_param = params.get('status')
        if status_param and (user.is_authenticated and user.is_staff):
            search = search.filter('term', status=status_param)

        # 按作者过滤
        author_id = params.get('author')
        if author_id:
            # ES 中有 author_username，但需要用 ID 过滤
            # 这里使用 MySQL 过滤（稍后处理）
            pass

        # 按精选过滤
        featured = params.get('featured')
        if featured:
            search = search.filter('term', featured=True)

        # 搜索（全文搜索）
        search_query = params.get('search')
        if search_query:
            from elasticsearch_dsl import Q
            q = Q(
                'multi_match',
                query=search_query,
                fields=['title^3', 'description^2', 'content'],
                fuzziness='AUTO'
            )
            search = search.query(q)

        # 排序
        sort_by = params.get('sort', '-published_at')
        search = search.sort(sort_by)

        # 分页
        page = int(params.get('page', 1))
        page_size = int(params.get('page_size', 20))
        start = (page - 1) * page_size
        end = start + page_size
        search = search[start:end]

        # 执行搜索
        try:
            # 对于管理员请求，强制刷新索引以确保获取最新数据
            # 对于普通用户请求，使用默认设置以提高性能
            if user.is_authenticated and user.is_staff:
                search = search.params(refresh=True)
            response = search.execute()
        except Exception as e:
            # ES 查询失败，降级到 MySQL
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"ES 查询失败，降级到 MySQL: {e}")
            return self._list_from_mysql(request, *args, **kwargs)

        # 2. 批量获取统计（避免 N+1 查询）
        article_ids = [hit.id for hit in response]
        stats_dict = self._get_batch_stats(article_ids)

        # 3. 合并数据并转换为前端期望的格式
        results = []
        for hit in response:
            data = hit.to_dict()

            # 构造嵌套的 author 对象（适配前端期望的 Article 格式）
            data['author'] = {
                'id': 0,  # ES 中没有 author_id
                'username': data.pop('author_username', ''),
                'nickname': data.pop('author_nickname', ''),
                'avatar': ''
            }

            # 构造嵌套的 category 对象
            category_name = data.pop('category_name', '')
            category_slug = data.pop('category_slug', '')
            data['category'] = {
                'id': 0,
                'slug': category_slug,
                'name': category_name,
                'category_type': category_slug  # ES 中 category_slug 就是 category_type
            }
            # 保留 category_type 字段（前端适配器需要）
            data['category_type'] = category_slug

            # 构造嵌套的 tags 数组
            tags_names = data.pop('tags_names', [])
            data['tags'] = [{'name': name, 'slug': name.lower()} for name in tags_names]

            # 合并统计
            stats = stats_dict.get(hit.id, {})
            data['view_count'] = stats.get('view_count', 0)
            data['like_count'] = stats.get('like_count', 0)
            data['comment_count'] = stats.get('comment_count', 0)
            results.append(data)

        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'results': results,
                'count': response.hits.total.value,
                'page': page,
                'page_size': page_size
            }
        })

    def _get_batch_stats(self, article_ids):
        """
        批量查询统计（单次 SQL + Redis 缓存 60 秒）

        使用缓存工具模块，支持缓存穿透防护和批量操作

        Args:
            article_ids: 文章 ID 列表

        Returns:
            dict: {article_id: {view_count, like_count, comment_count}}
        """
        if not article_ids:
            return {}

        # 使用标准化的缓存键
        cache_keys = {aid: CacheKeyBuilder.article_stats(aid) for aid in article_ids}
        cache_key_list = list(cache_keys.values())

        # 批量获取缓存
        cached_stats = get_many(cache_key_list)

        # 找出未命中的 ID
        missing_ids = [
            aid for aid in article_ids
            if cache_keys[aid] not in cached_stats
        ]

        # 批量查询数据库
        if missing_ids:
            stats = Article.objects.filter(
                id__in=missing_ids
            ).values('id', 'view_count', 'like_count', 'comment_count')

            # 准备缓存数据
            stats_dict = {}
            cache_data = {}
            for stat in stats:
                stats_dict[stat['id']] = {
                    'view_count': stat['view_count'],
                    'like_count': stat['like_count'],
                    'comment_count': stat['comment_count']
                }
                cache_data[CacheKeyBuilder.article_stats(stat['id'])] = stats_dict[stat['id']]

            # 批量写入缓存（60 秒 TTL）
            if cache_data:
                set_many(cache_data, ttl=60)
        else:
            stats_dict = {}

        # 合并缓存和数据库结果
        result = {}
        for aid in article_ids:
            cache_key = cache_keys[aid]
            if cache_key in cached_stats:
                # 处理可能的空值标记
                value = cached_stats[cache_key]
                result[aid] = value if value != "__NULL__" else {
                    'view_count': 0,
                    'like_count': 0,
                    'comment_count': 0
                }
            elif aid in stats_dict:
                result[aid] = stats_dict[aid]
            else:
                result[aid] = {
                    'view_count': 0,
                    'like_count': 0,
                    'comment_count': 0
                }

        return result

    def _list_from_mysql(self, request, *args, **kwargs):
        """降级方案：从 MySQL 查询（ES 查询失败时）"""
        queryset = self.filter_queryset(self.get_queryset())

        # 作者过滤在 MySQL 中处理
        author_id = request.query_params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        # 手动分页（与 ES 格式保持一致）
        from django.core.paginator import Paginator
        page = int(request.query_params.get('page', 1))
        page_size = int(request.query_params.get('page_size', 20))

        paginator = Paginator(queryset, page_size)
        try:
            page_obj = paginator.page(page)
        except:
            page_obj = paginator.page(1)

        serializer = self.get_serializer(page_obj.object_list, many=True)

        return Response({
            'code': 200,
            'message': 'success',
            'data': {
                'results': serializer.data,
                'count': paginator.count,
                'page': page,
                'page_size': page_size
            }
        })

    @swagger_auto_schema(
        operation_summary='获取文章详情',
        operation_description='根据 ID 或 slug 获取文章详细信息',
        responses={200: ArticleDetailSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """文章详情 - 支持 ID 或 slug 查找"""
        article = self.get_object()

        # 增加阅读量
        Article.objects.filter(pk=article.pk).update(view_count=F('view_count') + 1)

        serializer = self.get_serializer(article)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='创建文章',
        operation_description='创建新文章（需要登录）',
        request_body=ArticleCreateUpdateSerializer,
        responses={201: ArticleDetailSerializer}
    )
    def create(self, request, *args, **kwargs):
        """创建文章"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # 设置作者为当前用户
        serializer.validated_data['author'] = request.user
        self.perform_create(serializer)

        # 返回详情序列化器
        article = serializer.instance
        response_serializer = ArticleDetailSerializer(article)

        return Response({
            'code': 201,
            'message': '创建成功',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary='更新文章',
        operation_description='更新文章信息（需要登录）',
        request_body=ArticleCreateUpdateSerializer,
        responses={200: ArticleDetailSerializer}
    )
    def update(self, request, *args, **kwargs):
        """更新文章"""
        partial = kwargs.pop('partial', False)
        article = self.get_object()

        # 权限检查：只有作者或管理员可以编辑
        if article.author != request.user and not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '权限不足',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(article, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # 返回详情序列化器
        response_serializer = ArticleDetailSerializer(article)
        return Response({
            'code': 200,
            'message': '更新成功',
            'data': response_serializer.data
        })

    @swagger_auto_schema(
        operation_summary='删除文章',
        operation_description='删除文章（需要登录）',
        responses={204: '删除成功'}
    )
    def destroy(self, request, *args, **kwargs):
        """删除文章"""
        article = self.get_object()

        # 权限检查：只有作者或管理员可以删除
        if article.author != request.user and not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '权限不足',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(article)
        return Response({
            'code': 200,
            'message': '删除成功',
            'data': None
        })

    @swagger_auto_schema(
        operation_summary='获取精选文章',
        operation_description='获取所有精选文章列表',
        responses={200: ArticleDetailSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """精选文章"""
        queryset = self.get_queryset().filter(featured=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='获取热门文章',
        operation_description='按阅读量排序获取热门文章',
        responses={200: ArticleDetailSerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """热门文章"""
        queryset = self.get_queryset().order_by('-view_count')
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='创建文章版本',
        operation_description='为文章创建新版本（版本控制）',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'content': openapi.Schema(type=openapi.TYPE_STRING),
                'description': openapi.Schema(type=openapi.TYPE_STRING),
                'change_log': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={201: ArticleVersionSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def create_version(self, request, pk=None):
        """创建文章版本"""
        article = self.get_object()

        # 获取当前最新版本号
        latest_version = article.versions.first()
        next_version = (latest_version.version_number + 1) if latest_version else 1

        # 创建版本
        version = ArticleVersion.objects.create(
            article=article,
            version_number=next_version,
            title=request.data.get('title', article.title),
            content=request.data.get('content', article.content),
            description=request.data.get('description', article.description),
            edited_by=request.user,
            change_log=request.data.get('change_log', '')
        )

        serializer = ArticleVersionSerializer(version)
        return Response({
            'code': 201,
            'message': '版本创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary='获取文章版本列表',
        operation_description='获取文章的所有历史版本',
        responses={200: ArticleVersionSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """获取文章版本列表"""
        article = self.get_object()
        versions = article.versions.all()

        page = self.paginate_queryset(versions)
        serializer = ArticleVersionSerializer(versions, many=True)

        if page is not None:
            return self.get_paginated_response({
                'code': 200,
                'message': 'success',
                'data': serializer.data
            })

        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='点赞文章',
        operation_description='点赞指定的文章',
        responses={200: 'Success'},
    )
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞文章"""
        article = self.get_object()

        # 检查是否已经点赞
        if request.user.is_authenticated:
            like_exists = article.likes.filter(user=request.user).exists()
            if like_exists:
                return Response({
                    'code': 400,
                    'message': '已经点赞过了',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            # 创建点赞记录
            from .models import ArticleLike
            ArticleLike.objects.create(article=article, user=request.user)
        else:
            # 匿名用户基于 IP 点赞
            ip_address = self.get_client_ip(request)
            like_exists = article.likes.filter(ip_address=ip_address).exists()
            if like_exists:
                return Response({
                    'code': 400,
                    'message': '已经点赞过了',
                    'data': None
                }, status=status.HTTP_400_BAD_REQUEST)

            from .models import ArticleLike
            ArticleLike.objects.create(article=article, ip_address=ip_address)

        # 更新点赞数
        Article.objects.filter(pk=article.pk).update(like_count=F('like_count') + 1)
        article.refresh_from_db()

        return Response({
            'code': 200,
            'message': '点赞成功',
            'data': {
                'like_count': article.like_count,
                'liked': True
            }
        })

    @swagger_auto_schema(
        operation_summary='取消点赞文章',
        operation_description='取消点赞指定的文章',
        responses={200: 'Success'},
    )
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        """取消点赞文章"""
        article = self.get_object()

        if request.user.is_authenticated:
            # 删除用户点赞记录
            deleted_count, _ = article.likes.filter(user=request.user).delete()
        else:
            # 匿名用户基于 IP 删除点赞
            ip_address = self.get_client_ip(request)
            deleted_count, _ = article.likes.filter(ip_address=ip_address).delete()

        if deleted_count == 0:
            return Response({
                'code': 400,
                'message': '还未点赞过',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 更新点赞数
        Article.objects.filter(pk=article.pk).update(like_count=F('like_count') - 1)
        article.refresh_from_db()

        return Response({
            'code': 200,
            'message': '取消点赞成功',
            'data': {
                'like_count': article.like_count,
                'liked': False
            }
        })

    @swagger_auto_schema(
        operation_summary='获取相关文章',
        operation_description='基于标签相似度推荐相关文章',
        responses={200: ArticleListSerializer(many=True)},
    )
    @action(detail=True, methods=['get'])
    def related(self, request, pk=None):
        """获取相关文章"""
        article = self.get_object()
        limit = int(request.query_params.get('limit', 4))

        # 获取当前文章的所有标签 ID
        article_tag_ids = list(article.tags.values_list('id', flat=True))

        if not article_tag_ids:
            # 如果没有标签，返回同分类的其他文章
            related = Article.objects.filter(
                category=article.category,
                status='published'
            ).exclude(pk=article.pk).select_related('author', 'category').prefetch_related('tags')[:limit]
        else:
            # 使用数据库聚合计算共同标签数量，避免 N+1 问题
            from django.db.models import Count, Q

            # 找出有共同标签的文章，按共同标签数量排序
            related = (
                Article.objects.filter(
                    status='published',
                    tags__id__in=article_tag_ids
                )
                .exclude(pk=article.pk)
                .annotate(common_tags=Count('tags', filter=Q(tags__id__in=article_tag_ids)))
                .order_by('-common_tags', '-view_count')
                .select_related('author', 'category')
                .prefetch_related('tags')[:limit]
            )

        serializer = ArticleListSerializer(related, many=True)

        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })


"""
图片上传视图
"""
import os
import uuid
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods


@csrf_exempt
def image_upload_view(request):
    """
    图片上传视图
    支持拖拽上传和粘贴上传
    支持按分类目录保存：blog、projects、life
    包含速率限制：每分钟最多10次上传
    """
    # 获取客户端标识（IP地址或用户ID）
    user_id = request.user.id if request.user.is_authenticated else None
    client_ip = request.META.get('REMOTE_ADDR')
    identifier = f"user_{user_id}" if user_id else f"ip_{client_ip}"

    # 使用统一的速率限制工具
    allowed, remaining = RateLimiter.check_rate_limit(
        identifier=identifier,
        action="image_upload",
        max_requests=10,
        period=60
    )
    if not allowed:
        response = JsonResponse({
            'code': 429,
            'message': '上传过于频繁，请稍后再试',
            'data': None
        }, status=429)
        response['Access-Control-Allow-Origin'] = '*'
        response['X-RateLimit-Remaining'] = str(remaining)
        return response

    # 处理 OPTIONS 预检请求
    if request.method == 'OPTIONS':
        response = HttpResponse()
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
        response['Access-Control-Max-Age'] = '86400'
        return response

    # 只处理 POST 请求
    if request.method != 'POST':
        response = JsonResponse({
            'code': 405,
            'message': '请求方法不允许',
            'data': None
        }, status=405)
        response['Access-Control-Allow-Origin'] = '*'
        return response

    if 'file' not in request.FILES:
        response = JsonResponse({
            'code': 400,
            'message': '没有上传文件',
            'data': None
        }, status=400)
        response['Access-Control-Allow-Origin'] = '*'
        return response

    file = request.FILES['file']

    # 验证文件类型
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        response = JsonResponse({
            'code': 400,
            'message': f'不支持的文件类型: {file.content_type}',
            'data': None
        }, status=400)
        response['Access-Control-Allow-Origin'] = '*'
        return response

    # 验证文件大小（限制 10MB）
    max_size = 10 * 1024 * 1024  # 10MB
    if file.size > max_size:
        response = JsonResponse({
            'code': 400,
            'message': f'文件过大，最大支持 10MB',
            'data': None
        }, status=400)
        response['Access-Control-Allow-Origin'] = '*'
        return response

    try:
        # 获取分类参数（用于组织目录）
        category = request.POST.get('category', 'general')
        # 安全化分类名称，只保留字母数字和连字符
        safe_category = ''.join(c for c in category if c.isalnum() or c in ('-', '_'))
        if not safe_category:
            safe_category = 'general'

        # 生成唯一文件名
        file_ext = os.path.splitext(file.name)[1]
        unique_filename = f"{uuid.uuid4().hex}{file_ext}"

        # 按分类和日期组织目录：uploads/images/{category}/YYYY/MM/DD/
        date_path = datetime.now().strftime('%Y/%m/%d')
        file_path = os.path.join(f'uploads/images/{safe_category}', date_path, unique_filename)

        # 保存文件
        save_path = default_storage.save(file_path, file)

        # 获取文件的访问 URL（使用完整的外部 URL）
        file_url = default_storage.url(save_path)
        # 构建完整的访问 URL
        full_url = f"{settings.SITE_URL}{file_url}"

        response = JsonResponse({
            'code': 200,
            'message': '上传成功',
            'data': {
                'url': full_url,
                'alt': file.name,
                'href': full_url  # 兼容 md-editor-v3
            }
        })
        response['Access-Control-Allow-Origin'] = '*'
        return response

    except Exception as e:
        response = JsonResponse({
            'code': 500,
            'message': f'上传失败: {str(e)}',
            'data': None
        }, status=500)
        response['Access-Control-Allow-Origin'] = '*'
        return response
