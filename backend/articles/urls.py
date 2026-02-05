"""
文章模块 URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from articles.views import ArticleViewSet, image_upload_view

router = DefaultRouter()
router.register(r'', ArticleViewSet, basename='article')

urlpatterns = [
    path('upload-image/', image_upload_view, name='upload_image'),
    path('', include(router.urls)),
]

app_name = 'articles'
