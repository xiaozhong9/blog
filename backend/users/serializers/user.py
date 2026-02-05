"""
用户序列化器
"""

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from users.models import User


class UserProfileSerializer(serializers.ModelSerializer):
    """用户详细信息序列化器"""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'nickname', 'avatar', 'bio',
                  'website', 'github_url', 'twitter_url', 'linkedin_url',
                  'skills', 'timeline', 'story', 'role', 'is_verified', 'articles_count',
                  'comments_count', 'full_name', 'created_at', 'updated_at')
        read_only_fields = ('id', 'username', 'role', 'is_verified',
                           'articles_count', 'comments_count',
                           'created_at', 'updated_at')


class UserUpdateSerializer(serializers.ModelSerializer):
    """用户更新序列化器"""

    class Meta:
        model = User
        fields = ('nickname', 'avatar', 'bio', 'website',
                  'github_url', 'twitter_url', 'linkedin_url',
                  'skills', 'timeline', 'story')


class ChangePasswordSerializer(serializers.Serializer):
    """修改密码序列化器"""

    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate_old_password(self, value):
        """验证旧密码"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('旧密码错误')
        return value

    def validate(self, attrs):
        """验证新密码确认"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': '两次输入的新密码不一致'
            })
        return attrs

    def save(self, **kwargs):
        """保存新密码"""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user
