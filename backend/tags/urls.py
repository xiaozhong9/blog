"""
标签模块 URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from tags.views import TagViewSet

router = DefaultRouter()
router.register(r'', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router.urls)),
]

app_name = 'tags'
