"""
认证相关序列化器
"""

from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from users.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """注册序列化器"""

    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'nickname')
        extra_kwargs = {
            'email': {'required': False}
        }

    def validate(self, attrs):
        """验证密码确认"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password': '两次输入的密码不一致'
            })
        return attrs

    def create(self, validated_data):
        """创建用户"""
        validated_data.pop('password_confirm')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            nickname=validated_data.get('nickname', '')
        )
        return user


class LoginSerializer(TokenObtainPairSerializer):
    """登录序列化器"""

    username = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """验证用户凭据"""
        username = attrs.get('username')
        password = attrs.get('password')

        # 支持用户名或邮箱登录
        user = authenticate(
            request=self.context.get('request'),
            username=username,
            password=password
        )

        if not user:
            raise serializers.ValidationError(
                '用户名或密码错误',
                code='authorization'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                '用户账号已被禁用',
                code='authorization'
            )

        # 添加自定义 token 响应
        data = super().validate(attrs)
        data['user'] = UserSerializer(user, context=self.context).data
        return data

    @classmethod
    def get_token(cls, user):
        """自定义 token"""
        token = super().get_token(user)
        # 添加自定义 claims
        token['username'] = user.username
        token['role'] = user.role
        return token


class UserSerializer(serializers.ModelSerializer):
    """用户基本信息序列化器"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'avatar', 'bio',
                  'website', 'role', 'is_verified', 'articles_count',
                  'comments_count', 'created_at')
        read_only_fields = ('id', 'role', 'is_verified', 'articles_count',
                           'comments_count', 'created_at')
