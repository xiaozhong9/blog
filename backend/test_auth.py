"""
测试认证和创建文章的脚本
"""
import requests
import json
import sys

# Windows 编码修复
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

BASE_URL = "http://localhost:8000/api"

def test_login():
    """测试登录"""
    print("=" * 50)
    print("[1] 测试登录")
    print("=" * 50)

    response = requests.post(
        f"{BASE_URL}/auth/login/",
        json={"username": "admin", "password": "admin123"}
    )

    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

    if response.status_code == 200:
        data = response.json()
        if 'data' in data:
            return data['data']['access'], data['data']['refresh']
    return None, None

def test_create_article(access_token):
    """测试创建文章"""
    print("\n" + "=" * 50)
    print("[2] 测试创建文章（带认证）")
    print("=" * 50)

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    # 获取 categories
    cats_response = requests.get(f"{BASE_URL}/categories/")
    categories = cats_response.json()
    print(f"\n可用分类: {json.dumps(categories, ensure_ascii=False, indent=2)}")

    # 找到 blog 分类的 ID
    category_id = None
    for cat in categories:
        if cat.get('category_type') == 'blog':
            category_id = cat['id']
            break

    if not category_id:
        print("[ERROR] 找不到 blog 分类")
        return

    print(f"\n使用分类ID: {category_id}")

    # 创建文章数据
    article_data = {
        "title": "测试文章",
        "slug": "test-article-123",
        "description": "这是一篇测试文章",
        "content": "# 测试内容\n\n这是测试文章的内容。",
        "category_id": category_id,
        "locale": "zh",
        "reading_time": 5,
        "status": "published",
        "featured": False,
        "keywords": "test,demo"
    }

    print(f"\n发送数据: {json.dumps(article_data, ensure_ascii=False, indent=2)}")

    response = requests.post(
        f"{BASE_URL}/articles/",
        headers=headers,
        json=article_data
    )

    print(f"\n状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

    return response.status_code == 201

def test_without_auth():
    """测试未认证创建"""
    print("\n" + "=" * 50)
    print("[3] 测试未认证创建（应该失败）")
    print("=" * 50)

    response = requests.post(
        f"{BASE_URL}/articles/",
        json={
            "title": "未认证测试",
            "description": "测试",
            "content": "测试"
        }
    )

    print(f"状态码: {response.status_code}")
    print(f"响应: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")

if __name__ == "__main__":
    try:
        # 测试未认证请求
        test_without_auth()

        # 测试登录
        access_token, refresh_token = test_login()

        if access_token:
            print(f"\n[SUCCESS] 登录成功！")
            print(f"Access Token: {access_token[:50]}...")

            # 测试创建文章
            success = test_create_article(access_token)

            if success:
                print("\n" + "=" * 50)
                print("[SUCCESS] 所有测试通过！")
                print("=" * 50)
            else:
                print("\n" + "=" * 50)
                print("[FAILED] 创建文章失败")
                print("=" * 50)
        else:
            print("\n[FAILED] 登录失败，请检查用户名和密码")
            print("默认用户名: admin")
            print("默认密码: admin123")

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] 无法连接到后端服务器")
        print("请确保后端正在运行: cd backend && python manage.py runserver")
    except Exception as e:
        print(f"\n[ERROR] 错误: {e}")
        import traceback
        traceback.print_exc()
