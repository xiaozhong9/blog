# Nano Banana - API 接口详细规范

> 本文档提供每个接口的详细请求/响应示例，供后端开发人员参考。

**版本**: v1.0.0
**基础路径**: `/api`
**Content-Type**: `application/json`

---

## 目录

1. [认证模块](#1-认证模块)
2. [文章管理](#2-文章管理)
3. [标签管理](#3-标签管理)
4. [统计与互动](#4-统计与互动)
5. [搜索功能](#5-搜索功能)

---

## 1. 认证模块

### 1.1 用户登录

**接口**: `POST /auth/login`

**请求示例**:
```http
POST /api/auth/login
Content-Type: application/json

{
  "password": "admin"
}
```

**成功响应** (200 OK):
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwidXNlcm5hbWUiOiJhZG1pbiIsImlhdCI6MTcwNDAzMjAwMDAsImV4cCI6MTcwNDA2ODgwMDAwfQ.xxx",
    "expiresIn": 86400,
    "user": {
      "id": 1,
      "username": "admin",
      "email": null,
      "avatar": null,
      "bio": null
    }
  }
}
```

**失败响应** (401 Unauthorized):
```json
{
  "code": 401,
  "message": "密码错误",
  "data": null
}
```

---

### 1.2 检查登录状态

**接口**: `GET /auth/status`

**请求示例**:
```http
GET /api/auth/status
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxx
```

**已登录响应** (200 OK):
```json
{
  "code": 200,
  "message": "已登录",
  "data": {
    "isLoggedIn": true,
    "user": {
      "id": 1,
      "username": "admin"
    }
  }
}
```

**未登录响应** (200 OK):
```json
{
  "code": 200,
  "message": "未登录",
  "data": {
    "isLoggedIn": false,
    "user": null
  }
}
```

---

### 1.3 用户登出

**接口**: `POST /auth/logout`

**请求示例**:
```http
POST /api/auth/logout
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxx
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

---

## 2. 文章管理

### 2.1 获取文章列表

**接口**: `GET /posts`

**查询参数**:
```
page          页码，默认 1
pageSize      每页数量，默认 10
category      分类筛选：blog/projects/life/notes
tags          标签筛选，逗号分隔："vue,typescript"
locale        语言筛选：zh/en
featured      是否只显示精选：true/false
draft         是否包含草稿：默认 false
search        搜索关键词
sortBy        排序字段：date/popularity/readingTime
sortOrder     排序方向：asc/desc
dateFrom      起始日期：YYYY-MM-DD
dateTo        结束日期：YYYY-MM-DD
```

**请求示例**:
```http
GET /api/posts?page=1&pageSize=10&category=blog&tags=vue,typescript&locale=zh&draft=false&sortBy=date&sortOrder=desc
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "id": 2,
        "slug": "vue3-composition-api",
        "title": "Vue 3 Composition API 深度解析",
        "description": "全面解析 Vue 3 Composition API 的使用方法、最佳实践和实战技巧。",
        "date": "2024-01-20",
        "tags": ["vue", "typescript", "tutorial"],
        "category": "blog",
        "locale": "zh",
        "readingTime": 12,
        "coverImage": null,
        "featured": true,
        "draft": false,
        "views": 150
      }
    ],
    "total": 17,
    "page": 1,
    "pageSize": 10,
    "totalPages": 2
  }
}
```

---

### 2.2 获取文章详情

**接口**: `GET /posts/{slug}`

**路径参数**:
- `slug`: 文章 URL 别名，如 `vue3-composition-api`

**请求示例**:
```http
GET /api/posts/vue3-composition-api
```

**成功响应** (200 OK):
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 2,
    "slug": "vue3-composition-api",
    "title": "Vue 3 Composition API 深度解析",
    "description": "全面解析 Vue 3 Composition API 的使用方法、最佳实践和实战技巧。",
    "content": "# Vue 3 Composition API\n\n## 简介\n\nVue 3 引入了 Composition API...",
    "coverImage": null,
    "category": "blog",
    "locale": "zh",
    "author": "Nano Banana",
    "featured": true,
    "draft": false,
    "readingTime": 12,
    "viewCount": 150,
    "likeCount": 25,
    "publishDate": "2024-01-20",
    "tags": ["vue", "typescript", "tutorial"],
    "createdAt": "2024-01-20T10:00:00",
    "updatedAt": "2024-01-20T10:00:00"
  }
}
```

**文章不存在** (404 Not Found):
```json
{
  "code": 404,
  "message": "文章不存在",
  "data": null
}
```

---

### 2.3 创建文章

**接口**: `POST /posts`

**权限**: 需要登录

**请求示例**:
```http
POST /api/posts
Authorization: Bearer <token>
Content-Type: application/json

{
  "slug": "new-article",
  "title": "新文章标题",
  "description": "这是文章的摘要描述",
  "content": "# 新文章\n\n这是文章的正文内容...",
  "category": "blog",
  "locale": "zh",
  "tags": ["vue", "前端开发"],
  "featured": false,
  "draft": false,
  "readingTime": 8,
  "publishDate": "2024-02-04"
}
```

**成功响应** (201 Created):
```json
{
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": 18,
    "slug": "new-article"
  }
}
```

**Slug 重复** (409 Conflict):
```json
{
  "code": 409,
  "message": "Slug 已存在",
  "data": null
}
```

**参数校验失败** (400 Bad Request):
```json
{
  "code": 400,
  "message": "请求参数错误",
  "data": {
    "errors": [
      {
        "field": "title",
        "message": "标题不能为空"
      },
      {
        "field": "content",
        "message": "内容不能为空"
      }
    ]
  }
}
```

---

### 2.4 更新文章

**接口**: `PUT /posts/{slug}`

**权限**: 需要登录

**路径参数**:
- `slug`: 文章 URL 别名

**请求示例**:
```http
PUT /api/posts/new-article
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "更新后的标题",
  "description": "更新后的摘要",
  "content": "更新后的内容...",
  "tags": ["vue", "typescript", "前端"],
  "featured": true,
  "draft": false
}
```

**成功响应** (200 OK):
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 18,
    "slug": "new-article",
    "updatedAt": "2024-02-04T15:30:00"
  }
}
```

---

### 2.5 删除文章

**接口**: `DELETE /posts/{slug}`

**权限**: 需要登录

**路径参数**:
- `slug`: 文章 URL 别名

**请求示例**:
```http
DELETE /api/posts/new-article
Authorization: Bearer <token>
```

**成功响应** (200 OK):
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

### 2.6 切换草稿状态

**接口**: `PATCH /posts/{slug}/draft`

**权限**: 需要登录

**路径参数**:
- `slug`: 文章 URL 别名

**请求示例**:
```http
PATCH /api/posts/new-article/draft
Authorization: Bearer <token>
Content-Type: application/json

{
  "draft": false
}
```

**成功响应** (200 OK):
```json
{
  "code": 200,
  "message": "状态更新成功",
  "data": {
    "slug": "new-article",
    "draft": false
  }
}
```

---

### 2.7 批量操作

**接口**: `POST /posts/batch`

**权限**: 需要登录

**请求示例**:
```http
POST /api/posts/batch
Authorization: Bearer <token>
Content-Type: application/json

{
  "action": "delete",
  "slugs": ["slug1", "slug2", "slug3"]
}
```

**action 可选值**:
- `delete`: 批量删除
- `publish`: 批量发布
- `draft`: 批量设为草稿

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "批量操作成功",
  "data": {
    "successCount": 3,
    "failedCount": 0,
    "failedItems": []
  }
}
```

---

## 3. 标签管理

### 3.1 获取所有标签

**接口**: `GET /tags`

**查询参数**:
```
locale  语言筛选：zh/en
```

**请求示例**:
```http
GET /api/tags?locale=zh
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "id": 1,
      "name": "Vue",
      "slug": "vue",
      "description": "Vue.js 相关文章",
      "count": 15
    },
    {
      "id": 2,
      "name": "TypeScript",
      "slug": "typescript",
      "description": "TypeScript 相关文章",
      "count": 8
    }
  ]
}
```

---

### 3.2 创建标签

**接口**: `POST /tags`

**权限**: 需要登录

**请求示例**:
```http
POST /api/tags
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "React",
  "slug": "react",
  "description": "React 相关文章"
}
```

**响应** (201 Created):
```json
{
  "code": 201,
  "message": "标签创建成功",
  "data": {
    "id": 3,
    "slug": "react"
  }
}
```

---

### 3.3 更新标签

**接口**: `PUT /tags/{id}`

**权限**: 需要登录

**请求示例**:
```http
PUT /api/tags/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Vue.js",
  "description": "Vue.js 框架相关"
}
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 1,
    "name": "Vue.js",
    "slug": "vue"
  }
}
```

---

### 3.4 删除标签

**接口**: `DELETE /tags/{id}`

**权限**: 需要登录

**请求示例**:
```http
DELETE /api/tags/1
Authorization: Bearer <token>
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

---

## 4. 统计与互动

### 4.1 增加浏览量

**接口**: `POST /posts/{slug}/view`

**请求示例**:
```http
POST /api/posts/vue3-composition-api/view
Content-Type: application/json

{
  "ipAddress": "127.0.0.1",
  "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)..."
}
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "记录成功",
  "data": {
    "viewCount": 151,
    "todayViewCount": 5
  }
}
```

**说明**:
- 客户端 IP 可选，后端会从请求头获取
- 同一 IP 同一天只计一次浏览

---

### 4.2 点赞/取消点赞

**接口**: `POST /posts/{slug}/like`

**权限**: 需要登录（可选，支持游客点赞）

**请求示例**:
```http
POST /api/posts/vue3-composition-api/like
Authorization: Bearer <token>
Content-Type: application/json

{
  "liked": true
}
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "likeCount": 26,
    "liked": true
  }
}
```

---

### 4.3 获取热门文章

**接口**: `GET /posts/popular`

**查询参数**:
```
limit     返回数量，默认 10
category  分类筛选
days      最近 N 天，默认 30
```

**请求示例**:
```http
GET /api/posts/popular?limit=5&category=blog&days=7
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "slug": "vue3-composition-api",
      "title": "Vue 3 Composition API 深度解析",
      "viewCount": 500,
      "likeCount": 45
    }
  ]
}
```

---

### 4.4 获取统计数据

**接口**: `GET /stats/dashboard`

**权限**: 需要登录

**请求示例**:
```http
GET /api/stats/dashboard
Authorization: Bearer <token>
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "totalPosts": 34,
    "blogCount": 17,
    "projectsCount": 8,
    "lifeCount": 9,
    "featuredCount": 7,
    "draftCount": 2,
    "totalViews": 5000,
    "todayViews": 150,
    "weekViews": 800,
    "totalLikes": 320,
    "todayLikes": 15
  }
}
```

---

### 4.5 获取相关文章推荐

**接口**: `GET /posts/{slug}/related`

**路径参数**:
- `slug`: 文章 URL 别名

**查询参数**:
```
limit  返回数量，默认 4
```

**请求示例**:
```http
GET /api/posts/vue3-composition-api/related?limit=4
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "slug": "pinia-state-management",
      "title": "Pinia 状态管理完全指南",
      "description": "从入门到精通...",
      "similarity": 0.75
    },
    {
      "slug": "vue-router-4-guide",
      "title": "Vue Router 4 路由管理详解",
      "description": "深入理解 Vue Router 4...",
      "similarity": 0.60
    }
  ]
}
```

**推荐算法**:
1. 计算共同标签数量
2. 按相似度排序
3. 排除当前文章
4. 同类优先

---

## 5. 搜索功能

### 5.1 全文搜索

**接口**: `GET /search`

**查询参数**:
```
q         搜索关键词，必填
page      页码，默认 1
pageSize  每页数量，默认 10
category  分类筛选
locale    语言筛选
```

**请求示例**:
```http
GET /api/search?q=Vue&page=1&pageSize=10&category=blog&locale=zh
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "搜索成功",
  "data": {
    "items": [
      {
        "slug": "vue3-composition-api",
        "title": "Vue 3 Composition API 深度解析",
        "description": "全面解析 <mark>Vue</mark> 3 Composition API 的使用方法...",
        "category": "blog",
        "tags": ["vue", "typescript", "tutorial"],
        "highlight": {
          "title": "<mark>Vue</mark> 3 Composition API 深度解析",
          "description": "全面解析 <mark>Vue</mark> 3 Composition API 的使用方法...",
          "content": "<mark>Vue</mark> 3 是..."
        },
        "score": 2.5
      }
    ],
    "total": 5,
    "page": 1,
    "pageSize": 10,
    "totalPages": 1
  }
}
```

**说明**:
- `highlight` 字段使用 `<mark>` 标签高亮匹配文本
- `score` 字段表示相关度分数

---

### 5.2 搜索建议

**接口**: `GET /search/suggest`

**查询参数**:
```
q         搜索关键词，必填
limit     返回数量，默认 5
```

**请求示例**:
```http
GET /search/suggest?q=vue&limit=5
```

**响应** (200 OK):
```json
{
  "code": 200,
  "message": "获取成功",
  "data": [
    {
      "type": "post",
      "slug": "vue3-composition-api",
      "title": "Vue 3 Composition API 深度解析",
      "category": "blog"
    },
    {
      "type": "tag",
      "slug": "vue",
      "name": "Vue",
      "count": 15
    }
  ]
}
```

---

## 6. 错误处理示例

### 6.1 401 Unauthorized

**场景**: Token 无效或过期

```json
{
  "code": 401,
  "message": "未认证，请先登录",
  "data": null
}
```

### 6.2 403 Forbidden

**场景**: 无权限访问

```json
{
  "code": 403,
  "message": "权限不足",
  "data": null
}
```

### 6.3 404 Not Found

**场景**: 资源不存在

```json
{
  "code": 404,
  "message": "文章不存在",
  "data": null
}
```

### 6.4 409 Conflict

**场景**: 资源冲突

```json
{
  "code": 409,
  "message": "Slug 已存在",
  "data": {
    "field": "slug",
    "value": "existing-slug"
  }
}
```

### 6.5 500 Internal Server Error

**场景**: 服务器错误

```json
{
  "code": 500,
  "message": "服务器内部错误",
  "data": {
    "errorId": "error_123456"
  }
}
```

---

## 7. 数据库设计

### 7.1 表结构总结

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| user | 用户表 | id, username, password, email, avatar |
| post | 文章表 | id, slug, title, content, category, draft, featured |
| tag | 标签表 | id, name, slug, description |
| post_tag | 文章标签关联表 | post_id, tag_id |
| view_log | 浏览记录表 | post_id, ip_address, user_agent |
| likes | 点赞记录表 | post_id, user_id, ip_address |

### 7.2 索引设计

```sql
-- post 表索引
CREATE INDEX idx_category_draft ON post(category, draft);
CREATE INDEX idx_publish_date ON post(publish_date DESC);
CREATE INDEX idx_view_count ON post(view_count DESC);

-- view_log 表索引
CREATE INDEX idx_post_viewed ON view_log(post_id, viewed_at DESC);

-- likes 表索引
CREATE INDEX idx_post_user ON likes(post_id, user_id);
```

---

## 8. 前端联调配置

### 8.1 环境变量

创建 `.env` 文件：

```env
# API 基础路径
VITE_API_URL=http://localhost:8080/api

# 是否使用 mock 数据（开发模式）
VITE_USE_MOCK=false
```

### 8.2 API 配置文件

创建 `src/api/config.ts`:

```typescript
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8080/api',
  timeout: 10000,
  withCredentials: true,
}

export const API_ENDPOINTS = {
  // 认证
  LOGIN: '/auth/login',
  LOGOUT: '/auth/logout',
  STATUS: '/auth/status',

  // 文章
  POSTS: '/posts',
  POST_DETAIL: (slug: string) => `/posts/${slug}`,
  CREATE_POST: '/posts',
  UPDATE_POST: (slug: string) => `/posts/${slug}`,
  DELETE_POST: (slug: string) => `/posts/${slug}`,
  TOGGLE_DRAFT: (slug: string) => `/posts/${slug}/draft`,

  // 标签
  TAGS: '/tags',
  TAG_DETAIL: (id: number) => `/tags/${id}`,
  CREATE_TAG: '/tags',
  UPDATE_TAG: (id: number) => `/tags/${id}`,
  DELETE_TAG: (id: number) => `/tags/${id}`,

  // 统计
  INCREMENT_VIEW: (slug: string) => `/posts/${slug}/view`,
  TOGGLE_LIKE: (slug: string) => `/posts/${slug}/like`,
  POPULAR_POSTS: '/posts/popular',
  DASHBOARD_STATS: '/stats/dashboard',

  // 搜索
  SEARCH: '/search',
  SEARCH_SUGGEST: '/search/suggest',

  // 相关文章
  RELATED_POSTS: (slug: string) => `/posts/${slug}/related`,
}
```

---

## 9. 开发测试指南

### 9.1 本地测试

**使用 curl 测试登录**:
```bash
curl -X POST http://localhost:8080/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"password": "admin"}'
```

**使用 curl 获取文章列表**:
```bash
curl -X GET "http://localhost:8080/api/posts?page=1&pageSize=10&category=blog&draft=false" \
  -H "Content-Type: application/json"
```

**使用 curl 创建文章**:
```bash
curl -X POST http://localhost:8080/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "slug": "test-post",
    "title": "测试文章",
    "description": "这是一篇测试文章",
    "content": "# 测试\n\n内容...",
    "category": "blog",
    "locale": "zh",
    "tags": ["test"],
    "featured": false,
    "draft": false,
    "readingTime": 5,
    "publishDate": "2024-02-04"
  }'
```

### 9.2 Postman 集合

已提供 Postman Collection 文件，包含所有接口的请求示例。

**导入步骤**:
1. 打开 Postman
2. 点击 Import
3. 选择导入文件，导入 `docs/api/postman_collection.json`
4. 设置环境变量：
   - `base_url`: `http://localhost:8080/api`
   - `token`: 登录后获取的 token

---

## 10. 性能要求

### 10.1 响应时间要求

| 接口类型 | 响应时间要求 |
|---------|--------------|
| 文章列表 | < 200ms |
| 文章详情 | < 100ms |
| 搜索接口 | < 500ms |
| 统计接口 | < 100ms |
| 登录接口 | < 500ms |

### 10.2 并发要求

- 支持 1000+ 并发请求
- 数据库连接池优化
- Redis 缓存热点数据
- Elasticsearch 优化搜索性能

---

## 11. 安全考虑

### 11.1 认证安全

- ✅ JWT Token 认证
- ✅ Token 过期时间：24小时
- ✅ 密码使用 BCrypt 加密存储
- ⏳ Token 刷新机制（待实现）

### 11.2 数据验证

- ✅ 输入参数校验
- ✅ SQL 注入防护（使用 JPA/Hibernate）
- ✅ XSS 防护（前端转义）
- ⏳ CSRF 防护（待实现）

### 11.3 权限控制

- ✅ 登录才能创建/编辑/删除
- ⏳ 基于角色的权限控制（待实现）

---

## 12. 附录

### 12.1 状态码对照表

| Code | Message | HTTP Status |
|------|---------|--------------|
| 200 | 操作成功 | 200 |
| 201 | 创建成功 | 201 |
| 204 | 删除成功 | 204 |
| 400 | 请求参数错误 | 400 |
| 401 | 未认证 | 401 |
| 403 | 无权限 | 403 |
| 404 | 资源不存在 | 404 |
| 409 | 资源冲突 | 409 |
| 500 | 服务器内部错误 | 500 |

### 12.2 日期时间格式

- 所有日期时间使用 ISO 8601 格式
- 示例：`2024-01-20T10:00:00`
- 日期格式：`YYYY-MM-DD`

### 12.3 枚举值说明

**category** (文章分类):
- `blog`: 博客文章
- `projects`: 项目展示
- `life`: 生活记录
- `notes`: 笔记

**locale** (语言):
- `zh`: 中文
- `en`: 英文

**sortBy** (排序字段):
- `date`: 发布日期
- `popularity`: 热度（浏览量）
- `readingTime`: 阅读时间

---

**文档结束** 📚
