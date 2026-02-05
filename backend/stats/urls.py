"""
统计模块 URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from stats.views import StatsViewSet

router = DefaultRouter()
router.register(r'', StatsViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]

app_name = 'stats'
