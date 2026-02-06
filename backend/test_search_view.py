"""测试搜索视图"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
django.setup()

from search.views import SearchView
from rest_framework.test import APIRequestFactory

# 创建模拟请求
factory = APIRequestFactory()
request = factory.get('/api/search/?q=test&page=1&page_size=10')

# 创建视图实例
view = SearchView.as_view()

try:
    response = view(request)
    print(f'Response status: {response.status_code}')
    print(f'Response data: {response.data}')
except Exception as e:
    import traceback
    print(f'Error: {e}')
    traceback.print_exc()
