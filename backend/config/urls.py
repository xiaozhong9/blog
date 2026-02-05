"""
主 URL 配置
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),

    # API 路由
    path('api/auth/', include('users.urls')),
    path('api/articles/', include('articles.urls')),
    path('api/categories/', include('categories.urls')),
    path('api/tags/', include('tags.urls')),
    path('api/comments/', include('comments.urls')),
    path('api/search/', include('search.urls')),
    path('api/stats/', include('stats.urls')),
]

# 开发环境下添加 Swagger 文档
# 暂时禁用，待修复 DEBUG 错误
# try:
#     from rest_framework import permissions
#     from drf_yasg.views import get_schema_view
#     from drf_yasg import openapi
#
#     schema_view = get_schema_view(
#         openapi.Info(
#             title='Nano Banana Blog API',
#             default_version='v1',
#             description='Nano Banana 博客系统后端 API 文档',
#         ),
#         public=True,
#         permission_classes=(permissions.AllowAny,),
#     )
#
#     urlpatterns += [
#         path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
#         path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
#     ]
# except ImportError:
#     pass

# 开发环境下提供静态文件服务
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
