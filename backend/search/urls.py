"""
搜索模块 URL 配置
"""

from django.urls import path
from search import views

urlpatterns = [
    path('', views.SearchView.as_view(), name='search'),
    path('suggest/', views.SearchSuggestView.as_view(), name='search-suggest'),
]

app_name = 'search'
