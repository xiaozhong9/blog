"""
评论视图
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.throttling import AnonRateThrottle
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import F
from django.utils import timezone
from utils import get_client_ip

from .models import Comment, CommentLike
from .serializers import CommentSerializer, CommentCreateSerializer


class CommentRateThrottle(AnonRateThrottle):
    """评论频率限制 - 游客每小时最多 3 条"""
    rate = '3/hour'
    scope = 'comment'


class CommentViewSet(ModelViewSet):
    """评论视图集"""

    queryset = Comment.objects.select_related('author', 'article', 'parent')
    # 应用评论频率限制
    throttle_classes = [CommentRateThrottle]

    def get_serializer_class(self):
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def get_permissions(self):
        """权限控制"""
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        elif self.action in ['like', 'unlike']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def get_queryset(self):
        """自定义查询集"""
        queryset = super().get_queryset()
        params = self.request.query_params

        # 只显示已审核通过的评论（非管理员）
        user = self.request.user
        if not user.is_authenticated or not user.is_staff:
            queryset = queryset.filter(status='approved')
        else:
            # 管理员可以按状态过滤
            status_param = params.get('status')
            if status_param:
                queryset = queryset.filter(status=status_param)

        # 按文章过滤
        article_id = params.get('article')
        if article_id:
            queryset = queryset.filter(article_id=article_id)

        # 按作者过滤
        author_id = params.get('author')
        if author_id:
            queryset = queryset.filter(author_id=author_id)

        # 只显示顶级评论（无父评论）
        top_level = params.get('top_level')
        if top_level == 'true':
            queryset = queryset.filter(parent__isnull=True)

        return queryset

    @swagger_auto_schema(
        operation_summary='获取评论列表',
        operation_description='支持按文章、作者过滤',
        responses={200: CommentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """评论列表 - 统一分页格式"""
        queryset = self.filter_queryset(self.get_queryset())

        # 手动分页（与文章列表保持一致）
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
        operation_summary='获取评论详情',
        operation_description='根据 ID 获取评论详细信息',
        responses={200: CommentSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """评论详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='创建评论',
        operation_description='创建新评论（支持访客和登录用户）',
        request_body=CommentCreateSerializer,
        responses={201: CommentSerializer}
    )
    def create(self, request, *args, **kwargs):
        """创建评论"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # 返回详情序列化器
        comment = serializer.instance
        response_serializer = CommentSerializer(comment)

        return Response({
            'code': 201,
            'message': '评论成功，等待审核',
            'data': response_serializer.data
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary='更新评论',
        operation_description='更新评论信息（需要登录，且只能更新自己的评论）',
        request_body=CommentSerializer,
        responses={200: CommentSerializer}
    )
    def update(self, request, *args, **kwargs):
        """更新评论"""
        partial = kwargs.pop('partial', False)
        comment = self.get_object()

        # 权限检查：只有作者或管理员可以编辑
        if comment.author != request.user and not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '权限不足',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = self.get_serializer(comment, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({
            'code': 200,
            'message': '更新成功',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='删除评论',
        operation_description='删除评论（需要登录，且只能删除自己的评论）。会级联删除所有子评论。',
        responses={200: '删除成功'}
    )
    def destroy(self, request, *args, **kwargs):
        """删除评论"""
        comment = self.get_object()

        # 权限检查：只有作者或管理员可以删除
        if comment.author != request.user and not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '权限不足',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        # 级联删除所有子评论
        deleted_count = self._delete_comment_recursive(comment)

        self.perform_destroy(comment)

        return Response({
            'code': 200,
            'message': f'删除成功（共删除 {deleted_count} 条评论）',
            'data': {'deleted_count': deleted_count}
        })

    def _delete_comment_recursive(self, comment):
        """递归删除评论及其所有子评论"""
        count = 0

        # 递归删除所有子评论
        for child in comment.replies.all():
            count += self._delete_comment_recursive(child)
            child.delete()

        # 计数（包括当前评论）
        count += 1

        return count

    @swagger_auto_schema(
        operation_summary='点赞评论',
        operation_description='为评论点赞（需要登录）',
        responses={200: '点赞成功'}
    )
    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        """点赞评论"""
        comment = self.get_object()

        # 检查是否已点赞
        if CommentLike.objects.filter(comment=comment, user=request.user).exists():
            return Response({
                'code': 400,
                'message': '已经点赞过了',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 创建点赞记录
        CommentLike.objects.create(comment=comment, user=request.user)

        # 增加点赞数并刷新对象
        Comment.objects.filter(pk=comment.pk).update(like_count=F('like_count') + 1)
        comment.refresh_from_db(fields=['like_count'])

        return Response({
            'code': 200,
            'message': '点赞成功',
            'data': {'like_count': comment.like_count}
        })

    @swagger_auto_schema(
        operation_summary='取消点赞',
        operation_description='取消评论点赞（需要登录）',
        responses={200: '取消成功'}
    )
    @action(detail=True, methods=['post'])
    def unlike(self, request, pk=None):
        """取消点赞"""
        comment = self.get_object()

        # 检查是否已点赞
        like = CommentLike.objects.filter(comment=comment, user=request.user).first()
        if not like:
            return Response({
                'code': 400,
                'message': '还未点赞',
                'data': None
            }, status=status.HTTP_400_BAD_REQUEST)

        # 删除点赞记录
        like.delete()

        # 减少点赞数并刷新对象
        Comment.objects.filter(pk=comment.pk).update(like_count=F('like_count') - 1)
        comment.refresh_from_db(fields=['like_count'])

        return Response({
            'code': 200,
            'message': '取消成功',
            'data': {'like_count': max(0, comment.like_count)}
        })

    @swagger_auto_schema(
        operation_summary='获取评论回复',
        operation_description='获取指定评论的所有回复',
        responses={200: CommentSerializer(many=True)}
    )
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """获取评论回复"""
        comment = self.get_object()
        replies = comment.replies.all().filter(status='approved')

        serializer = CommentSerializer(replies, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='审核通过评论',
        operation_description='管理员审核通过评论（需要管理员权限）',
        responses={200: CommentSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        """审核通过评论"""
        if not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '权限不足',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        comment = self.get_object()
        comment.status = 'approved'
        comment.approved_at = timezone.now()
        comment.save()

        serializer = CommentSerializer(comment)
        return Response({
            'code': 200,
            'message': '审核通过',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='拒绝评论',
        operation_description='管理员拒绝评论（需要管理员权限）',
        responses={200: CommentSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        """拒绝评论"""
        if not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '权限不足',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        comment = self.get_object()
        comment.status = 'deleted'
        comment.save()

        serializer = CommentSerializer(comment)
        return Response({
            'code': 200,
            'message': '已拒绝',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='标记为垃圾评论',
        operation_description='管理员将评论标记为垃圾评论（需要管理员权限）',
        responses={200: CommentSerializer}
    )
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def spam(self, request, pk=None):
        """标记为垃圾评论"""
        if not request.user.is_staff:
            return Response({
                'code': 403,
                'message': '权限不足',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        comment = self.get_object()
        comment.status = 'spam'
        comment.save()

        serializer = CommentSerializer(comment)
        return Response({
            'code': 200,
            'message': '已标记为垃圾评论',
            'data': serializer.data
        })
