"""
用户管理视图
"""

from rest_framework import status
from rest_framework.decorators import action, permission_classes as permission_classes_decorator
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.models import User
from users.serializers.user import (
    UserProfileSerializer,
    UserUpdateSerializer,
    ChangePasswordSerializer
)


class UserViewSet(ModelViewSet):
    """用户管理视图集"""

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        """动态设置权限"""
        # profile action 允许公开访问
        if self.action == 'profile':
            return [AllowAny()]
        return super().get_permissions()

    def get_serializer_class(self):
        """获取序列化器"""
        if self.action == 'retrieve':
            return UserProfileSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return UserUpdateSerializer
        return UserProfileSerializer

    @swagger_auto_schema(
        operation_summary='获取用户详情',
        operation_description='根据 ID 获取用户详细信息',
        responses={200: UserProfileSerializer}
    )
    def retrieve(self, request, pk=None):
        """获取用户详情"""
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })

    @swagger_auto_schema(
        operation_summary='更新用户信息',
        operation_description='更新当前用户的信息',
        responses={200: UserProfileSerializer}
    )
    def update(self, request, pk=None):
        """更新用户信息"""
        # 只允许更新自己的信息
        if str(request.user.id) != str(pk) and not request.user.is_admin():
            return Response({
                'code': 403,
                'message': '权限不足',
                'data': None
            }, status=status.HTTP_403_FORBIDDEN)

        user = request.user
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'code': 200,
            'message': '更新成功',
            'data': UserProfileSerializer(user).data
        })

    @swagger_auto_schema(
        operation_summary='修改密码',
        operation_description='修改当前用户密码',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['old_password', 'new_password', 'new_password_confirm'],
            properties={
                'old_password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
                'new_password_confirm': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
            }
        ),
        responses={200: openapi.Response(description='密码修改成功')}
    )
    @action(detail=False, methods=['post'], url_path='change-password')
    def change_password(self, request):
        """修改密码"""
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({
            'code': 200,
            'message': '密码修改成功',
            'data': None
        })

    @swagger_auto_schema(
        operation_summary='获取公开的个人信息',
        operation_description='获取站点管理员的公开信息，用于 About 页面',
        responses={200: UserProfileSerializer}
    )
    @action(detail=False, methods=['get'], url_path='profile')
    @permission_classes_decorator([AllowAny])  # 公开访问，不需要认证
    def profile(self, request):
        """获取公开的个人信息"""
        try:
            # 获取第一个管理员用户
            user = User.objects.filter(role__in=['admin', 'editor']).first()
            if not user:
                user = request.user if request.user.is_authenticated else None

            if not user:
                return Response({
                    'code': 404,
                    'message': '未找到用户信息',
                    'data': None
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = UserProfileSerializer(user)
            return Response({
                'code': 200,
                'message': 'success',
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'code': 500,
                'message': str(e),
                'data': None
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
