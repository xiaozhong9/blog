"""
测试创建文章的脚本
"""
import requests
import json

# 测试创建文章
response = requests.post(
    'http://localhost:8000/api/articles/',
    headers={
        'Authorization': 'Bearer YOUR_TOKEN_HERE',  # 替换为实际 token
        'Content-Type': 'application/json'
    },
    json={
        'title': '测试文章',
        'slug': 'test-article',
        'description': '这是一篇测试文章',
        'content': '# 测试内容\n\n这是测试文章的内容。',
        'category_id': 1,  # blog 分类
        'locale': 'zh',
        'reading_time': 5,
        'status': 'published',
        'featured': False
    }
)

print('Status:', response.status_code)
print('Response:', json.dumps(response.json(), ensure_ascii=False, indent=2))
