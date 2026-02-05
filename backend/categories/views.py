"""
分类视图
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(ModelViewSet):
    """分类视图集"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        """权限控制"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return []

    @swagger_auto_schema(
        operation_summary='获取分类列表',
        operation_description='获取所有分类',
        responses={200: CategorySerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        """分类列表"""
        # 按类型过滤
        category_type = request.query_params.get('type')
        queryset = self.get_queryset()

        if category_type:
            queryset = queryset.filter(category_type=category_type)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='获取分类详情',
        operation_description='根据 slug 获取分类详细信息',
        responses={200: CategorySerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """分类详情"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='创建分类',
        operation_description='创建新分类（需要登录）',
        request_body=CategorySerializer,
        responses={201: CategorySerializer}
    )
    def create(self, request, *args, **kwargs):
        """创建分类"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            'code': 201,
            'message': '创建成功',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        operation_summary='更新分类',
        operation_description='更新分类信息（需要登录）',
        request_body=CategorySerializer,
        responses={200: CategorySerializer}
    )
    def update(self, request, *args, **kwargs):
        """更新分类"""
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
        operation_summary='删除分类',
        operation_description='删除分类（需要登录）',
        responses={200: '删除成功'}
    )
    def destroy(self, request, *args, **kwargs):
        """删除分类"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'code': 200,
            'message': '删除成功',
            'data': None
        })
