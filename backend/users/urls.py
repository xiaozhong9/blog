"""
用户模块 URL 配置
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from users.views import (
    RegisterViewSet,
    LoginViewSet,
    LogoutViewSet,
    MeViewSet,
    UserViewSet,
    TokenRefreshViewCustom
)

router = DefaultRouter()
router.register(r'register', RegisterViewSet, basename='register')
router.register(r'login', LoginViewSet, basename='login')
router.register(r'logout', LogoutViewSet, basename='logout')
router.register(r'me', MeViewSet, basename='me')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('refresh/', TokenRefreshViewCustom.as_view(), name='token_refresh'),
]

app_name = 'users'
