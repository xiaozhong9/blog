"""
标签视图
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Tag
from .serializers import TagSerializer


class TagViewSet(ModelViewSet):
    """标签视图集"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer

    def get_permissions(self):
        """权限控制 - 读取操作允许匿名访问"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        # 读取操作允许匿名访问
        return [AllowAny()]

    @swagger_auto_schema(
        operation_summary='获取标签列表',
        operation_description='获取所有标签',
        responses={200: TagSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """标签列表"""
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='获取标签详情',
        operation_description='根据 slug 获取标签详细信息',
        responses={200: TagSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """标签详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='创建标签',
        operation_description='创建新标签（需要登录）',
        request_body=TagSerializer,
        responses={201: TagSerializer}
    )
    def create(self, request, *args, **kwargs):
        """创建标签"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'code': 201,
            'message': '创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary='更新标签',
        operation_description='更新标签信息（需要登录）',
        request_body=TagSerializer,
        responses={200: TagSerializer}
    )
    def update(self, request, *args, **kwargs):
        """更新标签"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            'code': 200,
            'message': '更新成功',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='删除标签',
        operation_description='删除标签（需要登录）',
        responses={200: '删除成功'}
    )
    def destroy(self, request, *args, **kwargs):
        """删除标签"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
