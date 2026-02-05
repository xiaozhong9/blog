"""
评论序列化器
"""

from rest_framework import serializers
from .models import Comment, CommentLike


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""

    author = serializers.SerializerMethodField()
    article_title = serializers.CharField(source='article.title', read_only=True)
    article_slug = serializers.CharField(source='article.slug', read_only=True)
    article_category = serializers.CharField(source='article.category_type', read_only=True)

    class Meta:
        model = Comment
        fields = (
            'id', 'article', 'article_title', 'article_slug', 'article_category',
            'author', 'guest_name', 'parent', 'content', 'is_markdown',
            'status', 'like_count', 'created_at', 'updated_at', 'approved_at'
        )
        read_only_fields = ('id', 'like_count', 'created_at', 'updated_at', 'approved_at')

    def get_author(self, obj):
        """获取作者信息"""
        if obj.author:
            return {
                'id': obj.author.id,
                'username': obj.author.username,
                'nickname': obj.author.nickname,
                'email': obj.author.email,
                'avatar': obj.author.avatar
            }
        return None


class CommentCreateSerializer(serializers.ModelSerializer):
    """评论创建序列化器"""

    class Meta:
        model = Comment
        fields = (
            'article', 'parent', 'content', 'guest_name',
            'guest_email', 'guest_url'
        )

    def create(self, validated_data):
        """创建评论"""
        request = self.context.get('request')

        # 前台评论（有 guest_name 的）不关联 author，作为纯访客评论
        # 这样可以保持匿名性
        has_guest_info = 'guest_name' in validated_data or 'guest_email' in validated_data

        if has_guest_info:
            # 访客评论：不关联 author
            if not validated_data.get('guest_name'):
                raise serializers.ValidationError({'guest_name': '访客名称必填'})
            if not validated_data.get('guest_email'):
                raise serializers.ValidationError({'guest_email': '访客邮箱必填'})
        else:
            # 后台管理或其他情况：必须已登录
            if not request or not request.user.is_authenticated:
                raise serializers.ValidationError({'author': '需要登录'})
            validated_data['author'] = request.user

        # 记录 IP 和 User Agent
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:255]

        return super().create(validated_data)

    def get_client_ip(self, request):
        """获取客户端 IP"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class CommentLikeSerializer(serializers.ModelSerializer):
    """评论点赞序列化器"""

    class Meta:
        model = CommentLike
        fields = ('id', 'comment', 'user', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')
