"""
测试文章删除功能
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

# 1. 登录获取 token
print("=== 1. 登录 ===")
login_response = requests.post(f"{BASE_URL}/auth/login/", json={
    "username": "admin",
    "password": "admin123"
})
login_data = login_response.json()
print(f"登录响应: {json.dumps(login_data, indent=2, ensure_ascii=False)}")

if login_data.get("code") != 200:
    print("登录失败!")
    exit(1)

token = login_data["data"]["access"]
print(f"获取到 token: {token[:50]}...")

# 2. 获取文章列表
print("\n=== 2. 获取文章列表 ===")
headers = {"Authorization": f"Bearer {token}"}
list_response = requests.get(f"{BASE_URL}/articles/?category=blog&page_size=10", headers=headers)
list_data = list_response.json()
print(f"文章列表响应: {json.dumps(list_data, indent=2, ensure_ascii=False)}")

if list_data.get("code") != 200:
    print("获取文章列表失败!")
    exit(1)

articles = list_data["data"]["results"]
if not articles:
    print("没有可删除的文章")
    exit(0)

# 选择第一篇文章进行测试
test_article = articles[0]
article_slug = test_article["slug"]
print(f"\n选择测试文章: slug={article_slug}, title={test_article['title']}")

# 3. 删除文章
print(f"\n=== 3. 删除文章 (slug={article_slug}) ===")
delete_response = requests.delete(f"{BASE_URL}/articles/{article_slug}/", headers=headers)
print(f"删除响应状态码: {delete_response.status_code}")
delete_data = delete_response.json()
print(f"删除响应: {json.dumps(delete_data, indent=2, ensure_ascii=False)}")

# 4. 验证删除结果
print(f"\n=== 4. 验证删除结果 ===")

# 检查数据库
import django
import os
import sys

# 添加 Django 项目路径
sys.path.insert(0, r"p:\workspace\blog\backend")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from articles.models import Article
from search.models import ArticleDocument

# 检查 MySQL
try:
    article = Article.objects.get(slug=article_slug)
    print(f"MySQL: 文章仍然存在 (ID={article.id})")
except Article.DoesNotExist:
    print(f"MySQL: 文章已成功删除")

# 检查 ES
try:
    doc = ArticleDocument.get(id=article.get("id"))
    print(f"ES: 文档仍然存在 (slug={doc.slug})")
except:
    print(f"ES: 文档已成功删除")

# 5. 再次获取列表验证
print(f"\n=== 5. 再次获取文章列表 ===")
list_response2 = requests.get(f"{BASE_URL}/articles/?category=blog&page_size=10", headers=headers)
list_data2 = list_response2.json()
articles2 = list_data2["data"]["results"]

# 检查被删除的文章是否还在列表中
still_exists = any(a.get("slug") == article_slug for a in articles2)
print(f"文章是否还在列表中: {'是 - 删除失败!' if still_exists else '否 - 删除成功!'}")

print(f"\n当前文章数量: {len(articles2)}")
