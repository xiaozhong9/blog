# Django 博客后端 API 测试文档

## 🎉 后端已完成并测试通过！

**服务器状态**: ✅ 运行中 (http://localhost:8000)
**测试数据**: ✅ 已创建

---

## 📊 测试数据统计

### 数据概览
- **用户数**: 3
- **分类数**: 3
- **标签数**: 5
- **文章数**: 4 (全部已发布，其中 3 篇精选)
- **评论数**: 3

### 测试账号
```
管理员: admin / admin123
普通用户: testuser / testpass123
```

---

## 🚀 API 端点测试

### 1️⃣ 用户认证 API

#### 注册
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "pass123",
    "password_confirm": "pass123",
    "email": "newuser@example.com"
  }'
```

#### 登录
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**响应示例**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "refresh": "...",
    "access": "...",
    "user": {...}
  }
}
```

---

### 2️⃣ 文章 API

#### 获取文章列表
```bash
curl http://localhost:8000/api/articles/
```

**响应**: 分页列表，包含文章详情、作者、分类、标签

#### 获取精选文章
```bash
curl http://localhost:8000/api/articles/featured/
```

#### 获取热门文章
```bash
curl http://localhost:8000/api/articles/popular/
```

#### 获取文章详情 (通过 ID)
```bash
curl http://localhost:8000/api/articles/1/
```

#### 创建文章 (需要登录)
```bash
curl -X POST http://localhost:8000/api/articles/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "新文章标题",
    "description": "文章描述",
    "content": "文章内容",
    "category_id": 1,
    "tag_ids": [1, 2],
    "status": "published"
  }'
```

---

### 3️⃣ 分类 API

#### 获取所有分类
```bash
curl http://localhost:8000/api/categories/
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "Tech Blog",
      "slug": "tech-blog",
      "category_type": "blog",
      "icon": "computer"
    }
  ]
}
```

#### 按类型过滤
```bash
curl http://localhost:8000/api/categories/?type=blog
```

---

### 4️⃣ 标签 API

#### 获取所有标签
```bash
curl http://localhost:8000/api/tags/
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "Python",
      "slug": "python",
      "color": "#306998"
    }
  ]
}
```

---

### 5️⃣ 评论 API

#### 获取评论列表
```bash
curl http://localhost:8000/api/comments/
```

#### 获取文章评论
```bash
curl http://localhost:8000/api/comments/?article=1
```

#### 创建评论
```bash
curl -X POST http://localhost:8000/api/comments/ \
  -H "Content-Type: application/json" \
  -d '{
    "article": 1,
    "content": "这是一条测试评论"
  }'
```

#### 点赞评论 (需要登录)
```bash
curl -X POST http://localhost:8000/api/comments/1/like/ \
  -H "Authorization: Bearer <access_token>"
```

---

### 6️⃣ 统计 API

#### 获取总览统计
```bash
curl http://localhost:8000/api/stats/overview/
```

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_articles": 4,
    "total_users": 3,
    "total_comments": 3,
    "total_views": 9196,
    "popular_categories": [...],
    "popular_tags": [...]
  }
}
```

#### 获取热门文章
```bash
# 全部时间
curl http://localhost:8000/api/stats/popular_articles/

# 最近一周
curl http://localhost:8000/api/stats/popular_articles/?period=week

# 最近一个月
curl http://localhost:8000/api/stats/popular_articles/?period=month
```

---

## 📝 已创建的测试数据

### 文章列表
| ID | 标题 | 分类 | 标签 | 状态 | 阅读 |
|----|------|------|------|------|------|
| 1 | Django REST Framework Tutorial | Tech Blog | Python, Django | 已发布 | 1524 |
| 2 | Vue 3 Composition API Guide | Tech Blog | Vue, JavaScript | 已发布 | 2341 |
| 3 | Docker Deployment Guide | Tech Blog | Docker | 已发布 | 1876 |
| 4 | Personal Blog Project | Projects | Python, Django, Vue | 已发布 | 3456 |

### 分类列表
| ID | 名称 | Slug | 类型 |
|----|------|------|------|
| 1 | Tech Blog | tech-blog | blog |
| 2 | Projects | projects | projects |
| 3 | Life | life | life |

### 标签列表
| ID | 名称 | Slug | 颜色 |
|----|------|------|------|
| 1 | Python | python | #306998 |
| 2 | Django | django | #092E20 |
| 3 | Vue | vue | #42B883 |
| 4 | JavaScript | javascript | #F7DF1E |
| 5 | Docker | docker | #2496ED |

---

## 🔑 重要提示

### 认证方式
使用 JWT Token 认证：
1. 调用登录接口获取 `access_token`
2. 在后续请求的 Header 中添加：
   ```
   Authorization: Bearer <access_token>
   ```

### 权限说明
- **公开访问**: 文章列表、详情、分类、标签、统计
- **需要登录**: 创建/更新/删除文章、创建评论、点赞
- **仅管理员**: 某些管理功能

### 分页
文章列表支持分页：
```
?page=1&page_size=10
```

### 过滤
文章列表支持多种过滤：
```
?category=tech-blog         # 按分类
?tag=python                 # 按标签
?locale=zh                  # 按语言
?search=Django              # 搜索
?author=1                   # 按作者
```

---

## 🎯 前后端联调步骤

### 1. 配置前端 API 地址
```typescript
// frontend/src/config/api.ts
export const API_BASE_URL = 'http://localhost:8000/api'
```

### 2. 配置 Axios 拦截器
```typescript
// 添加 Token 到请求头
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
```

### 3. 测试流程
1. ✅ 使用 `admin/admin123` 登录
2. ✅ 获取文章列表并展示
3. ✅ 点击文章查看详情
4. ✅ 测试评论功能
5. ✅ 测试统计页面

---

## 📚 相关文档

- **Django Admin**: http://localhost:8000/admin/
- **API 根路径**: http://localhost:8000/api/
- **项目 README**: [README.md](README.md)
- **进度文档**: [progress.md](progress.md)

---

**最后更新**: 2026-02-04
**状态**: ✅ 后端已完成，可以开始前后端联调
