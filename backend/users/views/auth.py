"""
认证相关视图
"""

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from users.serializers.auth import (
    RegisterSerializer,
    LoginSerializer,
    UserSerializer
)


class RegisterViewSet(ViewSet):
    """注册视图集"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='用户注册',
        operation_description='创建新用户账号',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password', 'password_confirm'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
                'password_confirm': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={201: openapi.Response(description='注册成功')}
    )
    def create(self, request):
        """用户注册"""
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # 自动登录并返回 token
        refresh = RefreshToken.for_user(user)

        return Response({
            'code': 201,
            'message': '注册成功',
            'data': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserSerializer(user).data
            }
        }, status=status.HTTP_201_CREATED)


class LoginViewSet(ViewSet):
    """登录视图集"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='用户登录',
        operation_description='使用用户名或邮箱登录',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING, format='password'),
            }
        ),
        responses={200: openapi.Response(description='登录成功')}
    )
    def create(self, request):
        """用户登录"""
        serializer = LoginSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        return Response({
            'code': 200,
            'message': '登录成功',
            'data': serializer.validated_data
        })


class LogoutViewSet(ViewSet):
    """登出视图集"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_summary='用户登出',
        operation_description='登出并刷新 token (加入黑名单)',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={200: openapi.Response(description='登出成功')}
    )
    def create(self, request):
        """用户登出"""
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass

        return Response({
            'code': 200,
            'message': '登出成功',
            'data': None
        })


class MeViewSet(ViewSet):
    """当前用户视图集"""

    permission_classes = []  # 已在 settings 中配置全局权限

    @swagger_auto_schema(
        operation_summary='获取当前用户信息',
        operation_description='获取已登录用户的详细信息',
        responses={200: UserSerializer}
    )
    def list(self, request):
        """获取当前用户信息"""
        if not request.user.is_authenticated:
            return Response({
                'code': 401,
                'message': '未登录',
                'data': None
            }, status=status.HTTP_401_UNAUTHORIZED)

        serializer = UserSerializer(request.user)
        return Response({
            'code': 200,
            'message': 'success',
            'data': serializer.data
        })


class TokenRefreshViewCustom(TokenRefreshView):
    """自定义 Token 刷新视图"""

    @swagger_auto_schema(
        operation_summary='刷新访问令牌',
        operation_description='使用 refresh token 获取新的 access token',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={200: openapi.Response(description='刷新成功')}
    )
    def post(self, request, *args, **kwargs):
        """刷新 token"""
        response = super().post(request, *args, **kwargs)

        # 包装响应格式
        return Response({
            'code': 200,
            'message': '刷新成功',
            'data': response.data
        })
