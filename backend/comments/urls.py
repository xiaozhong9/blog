"""
评论模块 URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from comments.views import CommentViewSet

router = DefaultRouter()
router.register(r'', CommentViewSet, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
]

app_name = 'comments'
