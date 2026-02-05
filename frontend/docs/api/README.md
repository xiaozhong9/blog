# Nano Banana - 后端 API 接口规范文档

> 本文档描述了 Nano Banana 个人博客系统的完整后端 API 接口规范，用于前后端联调和接口开发。

**文档版本**: v1.0.0
**最后更新**: 2026-02-04
**项目地址**: https://github.com/your-username/nano-banana

---

## 📋 目录

1. [项目概述](#项目概述)
2. [技术栈](#技术栈)
3. [数据模型](#数据模型)
4. [认证机制](#认证机制)
5. [API 接口规范](#api-接口规范)
6. [前端状态管理](#前端状态管理)
7. [错误处理](#错误处理)
8. [部署建议](#部署建议)

---

## 1. 项目概述

### 1.1 项目简介

Nano Banana 是一个现代化的个人博客系统，支持：

- 博客文章管理
- 项目展示
- 生活记录
- 多维度筛选和搜索
- 浏览统计和点赞
- 评论系统（基于 GitHub Discussions）

### 1.2 架构设计

```
┌─────────────────┐
│   前端 (Vue 3)    │
├─────────────────┤
│  API Gateway    │
├─────────────────┤
│  Spring Boot     │
│  ┌───────────┐  │
│  │Controller │  │
│  ├───────────┤  │
│  │  Service  │  │
│  ├───────────┤  │
│  │Repository│  │
│  └───────────┘  │
├─────────────────┤
│  ┌───────────┐  │
│  │  MySQL   │  │
│  ├───────────┤  │
│  │   Redis   │  │
│  ├───────────┤  │
│  │  Elastic  │  │
│  │  Search   │  │
│  └───────────┘  │
└─────────────────┘
```

---

## 2. 技术栈

### 2.1 前端技术栈

- **框架**: Vue 3.4+ (Composition API + Script Setup)
- **语言**: TypeScript 5.0+
- **构建工具**: Vite 5.0+
- **UI 框架**: Tailwind CSS 3.4+
- **状态管理**: Pinia
- **路由**: Vue Router 4.x (unplugin-vue-router)
- **HTTP 客户端**: Axios (待实现)

### 2.2 后端技术栈

- **框架**: Spring Boot 3.x
- **语言**: Java 17+
- **数据库**: MySQL 8.0+
- **缓存**: Redis 7.x
- **搜索引擎**: Elasticsearch 8.x
- **API 文档**: Swagger/OpenAPI 3.0
- **安全**: Spring Security + JWT

---

## 3. 数据模型

### 3.1 核心实体

#### 3.1.1 User (用户表)

```sql
CREATE TABLE `user` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '用户ID',
  `username` VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
  `password` VARCHAR(255) NOT NULL COMMENT '密码（加密）',
  `email` VARCHAR(100) COMMENT '邮箱',
  `avatar` VARCHAR(500) COMMENT '头像URL',
  `bio` TEXT COMMENT '个人简介',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_username (`username`),
  INDEX idx_email (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

#### 3.1.2 Post (文章/内容表)

```sql
CREATE TABLE `post` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '文章ID',
  `slug` VARCHAR(255) NOT NULL UNIQUE COMMENT 'URL别名',
  `title` VARCHAR(255) NOT NULL COMMENT '标题',
  `description` TEXT COMMENT '摘要',
  `content` LONGTEXT NOT NULL COMMENT '内容（Markdown）',
  `cover_image` VARCHAR(500) COMMENT '封面图',
  `category` VARCHAR(50) NOT NULL COMMENT '分类：blog/projects/life/notes',
  `locale` VARCHAR(10) NOT NULL DEFAULT 'zh' COMMENT '语言：zh/en',
  `author` VARCHAR(100) NOT NULL DEFAULT 'Nano Banana' COMMENT '作者',
  `featured` BOOLEAN DEFAULT FALSE COMMENT '是否精选',
  `draft` BOOLEAN DEFAULT FALSE COMMENT '是否草稿',
  `reading_time` INT DEFAULT 5 COMMENT '阅读时间（分钟）',
  `view_count` BIGINT DEFAULT 0 COMMENT '浏览次数',
  `like_count` INT DEFAULT 0 COMMENT '点赞数',
  `publish_date` DATE COMMENT '发布日期',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  INDEX idx_slug (`slug`),
  INDEX idx_category (`category`),
  INDEX idx_locale (`locale`),
  INDEX idx_featured (`featured`),
  INDEX idx_draft (`draft`),
  INDEX idx_publish_date (`publish_date`),
  INDEX idx_created_at (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章表';
```

#### 3.1.3 Tag (标签表)

```sql
CREATE TABLE `tag` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '标签ID',
  `name` VARCHAR(50) NOT NULL UNIQUE COMMENT '标签名称',
  `slug` VARCHAR(100) NOT NULL UNIQUE COMMENT 'URL别名',
  `description` VARCHAR(255) COMMENT '标签描述',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  INDEX idx_name (`name`),
  INDEX idx_slug (`slug`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='标签表';
```

#### 3.1.4 PostTag (文章标签关联表)

```sql
CREATE TABLE `post_tag` (
  `post_id` BIGINT NOT NULL COMMENT '文章ID',
  `tag_id` BIGINT NOT NULL COMMENT '标签ID',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  PRIMARY KEY (`post_id`, `tag_id`),
  FOREIGN KEY (`post_id`) REFERENCES `post`(`id`) ON DELETE CASCADE,
  FOREIGN KEY (`tag_id`) REFERENCES `tag`(`id`) ON DELETE CASCADE,
  INDEX idx_post_id (`post_id`),
  INDEX idx_tag_id (`tag_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='文章标签关联表';
```

#### 3.1.5 ViewLog (浏览记录表)

```sql
CREATE TABLE `view_log` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '记录ID',
  `post_id` BIGINT NOT NULL COMMENT '文章ID',
  `ip_address` VARCHAR(45) COMMENT 'IP地址',
  `user_agent` VARCHAR(500) COMMENT 'User Agent',
  `viewed_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '浏览时间',
  INDEX idx_post_id (`post_id`),
  INDEX idx_viewed_at (`viewed_at`),
  FOREIGN KEY (`post_id`) REFERENCES `post`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='浏览记录表';
```

#### 3.1.6 Like (点赞记录表)

```sql
CREATE TABLE `likes` (
  `id` BIGINT PRIMARY KEY AUTO_INCREMENT COMMENT '点赞ID',
  `post_id` BIGINT NOT NULL COMMENT '文章ID',
  `user_id` BIGINT COMMENT '用户ID（NULL表示游客）',
  `ip_address` VARCHAR(45) COMMENT 'IP地址',
  `created_at` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '点赞时间',
  PRIMARY KEY (`post_id`, `user_id`, `ip_address`),
  FOREIGN KEY (`post_id`) REFERENCES `post`(`id`) ON DELETE CASCADE,
  INDEX idx_post_id (`post_id`),
  INDEX idx_user_id (`user_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='点赞记录表';
```

### 3.2 数据模型定义

#### 3.2.1 Post (前端对应)

```typescript
interface Post {
  id: number
  slug: string
  title: string
  description: string
  content: string
  coverImage?: string
  category: 'blog' | 'projects' | 'life' | 'notes'
  locale: 'zh' | 'en'
  author: string
  featured: boolean
  draft: boolean
  readingTime: number
  viewCount: number
  likeCount: number
  publishDate: string // ISO date format: YYYY-MM-DD
  tags: string[]
  createdAt: string
  updatedAt: string
}

interface PostSummary {
  slug: string
  title: string
  description: string
  date: string // publishDate
  tags: string[]
  category: 'blog' | 'projects' | 'life' | 'notes'
  locale: 'zh' | 'en'
  readingTime?: number
  image?: string
  featured: boolean
  draft: boolean
  views?: number // 同 viewCount
}
```

---

## 4. 认证机制

### 4.1 简单密码认证（当前实现）

当前系统使用简单的密码认证方式：

- **登录接口**: `POST /api/auth/login`
- **请求体**:
  ```json
  {
    "password": "admin"
  }
  ```
- **响应**:
  ```json
  {
    "code": 200,
    "message": "登录成功",
    "data": {
      "token": "jwt_token_here"
    }
  }
  ```

### 4.2 JWT Token 机制（推荐）

**Token 结构**:

```json
{
  "sub": "user_id",
  "username": "admin",
  "iat": 1234567890,
  "exp": 1234567890
}
```

**Token 传递方式**:

```
Authorization: Bearer <token>
```

---

## 5. API 接口规范

### 5.1 基础规范

#### 5.1.1 请求格式

- **基础路径**: `/api`
- **Content-Type**: `application/json`
- **字符编码**: UTF-8

#### 5.1.2 响应格式

**成功响应**:

```json
{
  "code": 200,
  "message": "操作成功",
  "data": { /* 响应数据 */ }
}
```

**错误响应**:

```json
{
  "code": 400,
  "message": "错误描述",
  "data": null
}
```

**常用状态码**:

- `200`: 成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 无权限
- `404`: 资源不存在
- `500`: 服务器内部错误

---

### 5.2 认证接口

#### 5.2.1 用户登录

```
POST /api/auth/login
```

**请求体**:

```json
{
  "password": "admin"
}
```

**响应**:

```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "email": null
    }
  }
}
```

**错误示例**:

```json
{
  "code": 401,
  "message": "密码错误",
  "data": null
}
```

#### 5.2.2 检查登录状态

```
GET /api/auth/status
```

**请求头**:

```
Authorization: Bearer <token>
```

**响应**:

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

#### 5.2.3 登出

```
POST /api/auth/logout
```

**请求头**:

```
Authorization: Bearer <token>
```

**响应**:

```json
{
  "code": 200,
  "message": "登出成功",
  "data": null
}
```

---

### 5.3 文章接口

#### 5.3.1 获取文章列表（分页）

```
GET /api/posts
```

**查询参数**:

| 参数      | 类型    | 必填 | 说明                                  | 示例           |
| --------- | ------- | ---- | ------------------------------------- | -------------- |
| page      | int     | 否   | 页码，从1开始                         | 1              |
| pageSize  | int     | 否   | 每页数量，默认10                      | 10             |
| category  | string  | 否   | 分类筛选                              | blog           |
| tags      | string  | 否   | 标签筛选（逗号分隔）                  | vue,typescript |
| locale    | string  | 否   | 语言筛选                              | zh             |
| featured  | boolean | 否   | 只显示精选                            | true           |
| draft     | boolean | 否   | 包含草稿，默认false                   | false          |
| search    | string  | 否   | 搜索关键词                            | Vue            |
| sortBy    | string  | 否   | 排序字段：date/popularity/readingTime | date           |
| sortOrder | string  | 否   | 排序方向：asc/desc                    | desc           |
| dateFrom  | string  | 否   | 起始日期                              | 2024-01-01     |
| dateTo    | string  | 否   | 结束日期                              | 2024-12-31     |

**响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "items": [
      {
        "slug": "vue3-composition-api",
        "title": "Vue 3 Composition API 深度解析",
        "description": "全面解析 Vue 3 Composition API 的使用方法...",
        "date": "2024-01-20",
        "tags": ["vue", "typescript", "tutorial"],
        "category": "blog",
        "locale": "zh",
        "readingTime": 12,
        "image": null,
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

#### 5.3.2 根据 slug 获取文章详情

```
GET /api/posts/{slug}
```

**路径参数**:

- `slug`: 文章的 URL 别名

**响应**:

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "id": 2,
    "slug": "vue3-composition-api",
    "title": "Vue 3 Composition API 深度解析",
    "description": "全面解析 Vue 3 Composition API 的使用方法...",
    "content": "# Vue 3 Composition API\n\n## 简介\n\n...",
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

#### 5.3.3 创建文章

```
POST /api/posts
```

**请求头**:

```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:

```json
{
  "slug": "new-post",
  "title": "新文章标题",
  "description": "文章摘要",
  "content": "# 文章内容\n\n这是文章的正文...",
  "category": "blog",
  "locale": "zh",
  "tags": ["vue", "前端"],
  "featured": false,
  "draft": false,
  "readingTime": 10,
  "publishDate": "2024-02-04"
}
```

**响应**:

```json
{
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": 18,
    "slug": "new-post"
  }
}
```

#### 5.3.4 更新文章

```
PUT /api/posts/{slug}
```

**请求头**:

```
Authorization: Bearer <token>
Content-Type: application/json
```

**路径参数**:

- `slug`: 文章的 URL 别名

**请求体**:

```json
{
  "title": "更新后的标题",
  "description": "更新后的摘要",
  "content": "更新后的内容...",
  "category": "blog",
  "tags": ["vue", "typescript"],
  "featured": true,
  "draft": false
}
```

**响应**:

```json
{
  "code": 200,
  "message": "更新成功",
  "data": {
    "id": 18,
    "slug": "new-post"
  }
}
```

#### 5.3.5 删除文章

```
DELETE /api/posts/{slug}
```

**请求头**:

```
Authorization: Bearer <token>
```

**路径参数**:

- `slug`: 文章的 URL 别名

**响应**:

```json
{
  "code": 200,
  "message": "删除成功",
  "data": null
}
```

#### 5.3.6 切换草稿/发布状态

```
PATCH /api/posts/{slug}/draft
```

**请求头**:

```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体**:

```json
{
  "draft": false
}
```

**响应**:

```json
{
  "code": 200,
  "message": "状态更新成功",
  "data": {
    "slug": "new-post",
    "draft": false
  }
}
```

---

### 5.4 标签接口

#### 5.4.1 获取所有标签

```
GET /api/tags
```

**查询参数**:

| 参数   | 类型   | 必填 | 说明     |
| ------ | ------ | ---- | -------- |
| locale | string | 否   | 语言筛选 |

**响应**:

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

### 5.5 统计接口

#### 5.5.1 增加浏览量

```
POST /api/posts/{slug}/view
```

**请求体** (可选):

```json
{
  "ipAddress": "127.0.0.1",
  "userAgent": "Mozilla/5.0..."
}
```

**响应**:

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

- 同一 IP 同一天只计一次
- 前端可调用，后端基于 IP 和日期去重

#### 5.5.2 点赞/取消点赞

```
POST /api/posts/{slug}/like
```

**请求头**:

```
Authorization: Bearer <token>
```

**请求体**:

```json
{
  "liked": true
}
```

**响应**:

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

#### 5.5.3 获取热门文章

```
GET /api/posts/popular
```

**查询参数**:

| 参数     | 类型   | 必填 | 说明     | 默认值 |
| -------- | ------ | ---- | -------- | ------ |
| limit    | int    | 否   | 返回数量 | 10     |
| category | string | 否   | 分类筛选 | -      |
| days     | int    | 否   | 最近N天  | 30     |

**响应**:

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

### 5.6 搜索接口

#### 5.6.1 全文搜索

```
GET /api/search
```

**查询参数**:

| 参数     | 类型   | 必填 | 说明       | 示例 |
| -------- | ------ | ---- | ---------- | ---- |
| q        | string | 是   | 搜索关键词 | Vue  |
| page     | int    | 否   | 页码       | 1    |
| pageSize | int    | 否   | 每页数量   | 10   |
| category | string | 否   | 分类筛选   | blog |
| locale   | string | 否   | 语言筛选   | zh   |

**响应**:

```json
{
  "code": 200,
  "message": "搜索成功",
  "data": {
    "items": [
      {
        "slug": "vue3-composition-api",
        "title": "Vue 3 Composition API 深度解析",
        "description": "全面解析 Vue 3...",
        "category": "blog",
        "tags": ["vue", "typescript"],
        "highlight": {
          "title": "<mark>Vue</mark> 3 Composition API...",
          "content": "<mark>Vue</mark> 3 是..."
        }
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

- `highlight` 字段包含高亮后的文本
- 使用 `<mark>` 标签标记匹配的关键词

---

### 5.7 相关文章推荐

```
GET /api/posts/{slug}/related
```

**路径参数**:

- `slug`: 文章的 URL 别名

**查询参数**:

| 参数  | 类型 | 必填 | 说明     | 默认值 |
| ----- | ---- | ---- | -------- | ------ |
| limit | int  | 否   | 返回数量 | 4      |

**响应**:

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
    }
  ]
}
```

**推荐算法**:

- 基于标签匹配度计算相似度
- 同类文章优先
- 排除当前文章

---

### 5.8 数据统计接口

#### 5.8.1 获取统计数据

```
GET /api/stats/dashboard
```

**响应**:

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
    "totalViews": 5000,
    "todayViews": 150,
    "totalLikes": 320
  }
}
```

---

## 6. 前端状态管理

### 6.1 Content Store (Pinia)

**位置**: `src/stores/content.ts`

**核心状态**:

```typescript
interface ContentState {
  posts: PostSummary[]        // 所有文章
  currentPost: Post | null     // 当前查看的文章
  loading: boolean            // 加载状态
  error: Error | null          // 错误信息
}
```

**核心方法**:

```typescript
// 获取所有文章
loadAllContent(): void

// 根据 slug 获取文章详情
getPostBySlug(slug: string): Promise<Post>

// 筛选文章
filterPosts(filter: ContentFilter): PostSummary[]

// 分页查询
getPaginatedPosts(params: {
  page: number
  pageSize: number
  category?: string
  search?: string
}): PaginatedResult

// 创建文章
createPost(data: CreatePostDto): Promise<PostSummary>

// 更新文章
updatePost(slug: string, data: UpdatePostDto): Promise<PostSummary>

// 删除文章
deletePost(slug: string): Promise<boolean>

// 增加浏览量
incrementViews(slug: string): void

// 获取热门文章
getPopularPosts(limit?: number): PostSummary[]
```

### 6.2 Admin Store (Pinia)

**位置**: `src/stores/admin.ts`

**核心状态**:

```typescript
interface AdminState {
  isLoggedIn: boolean
}
```

**核心方法**:

```typescript
// 登录
login(password: string): boolean

// 登出
logout(): void

// 检查登录状态
checkLoginStatus(): void
```

---

## 7. 错误处理

### 7.1 错误码规范

| 错误码 | 说明                 | HTTP状态码 |
| ------ | -------------------- | ---------- |
| 200    | 成功                 | 200        |
| 400    | 请求参数错误         | 400        |
| 401    | 未认证               | 401        |
| 403    | 无权限               | 403        |
| 404    | 资源不存在           | 404        |
| 409    | 冲突（如 slug 重复） | 409        |
| 500    | 服务器内部错误       | 500        |

### 7.2 错误响应示例

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
        "field": "slug",
        "message": "slug 已存在"
      }
    ]
  }
}
```

---

## 8. 部署建议

### 8.1 环境变量

**后端 application.yml**:

```yaml
spring:
  datasource:
    url: jdbc:mysql://localhost:3306/nano_banana?useSSL=false&serverTimezone=UTC
    username: root
    password: your_password
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true

  redis:
    host: localhost
    port: 6379
    password: your_redis_password

  elasticsearch:
    uris: http://localhost:9200

  security:
    jwt:
      secret: your-secret-key-at-least-256-bits
      expiration: 86400000 # 24小时
```

### 8.2 CORS 配置

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins("http://localhost:5173")
                .allowedMethods("GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS")
                .allowedHeaders("*")
                .allowCredentials(true);
    }
}
```

### 8.3 API 配置

```java
@Configuration
public class ApiConfig {
    @Bean
    public OpenAPICustomizer openAPICustomizer() {
        return openApi -> openApi
            .info(new Info()
                .title("Nano Banana API")
                .version("1.0.0")
                .description("Nano Banana 个人博客系统接口文档"))
            .addServersItem(new Server()
                .url("http://localhost:8080")
                .description("开发环境"));
    }
}
```

---

## 9. 前端调用示例

### 9.1 使用 Axios (推荐)

**配置 axios 实例** (`src/api/client.ts`):

```typescript
import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8080/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// 请求拦截器：添加 token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('nano_banana_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：统一处理错误
apiClient.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      // 清除 token，跳转到登录页
      localStorage.removeItem('nano_banana_token')
      window.location.href = '/admin/login'
    }
    return Promise.reject(error)
  }
)

export default apiClient
```

### 9.2 API 调用示例

```typescript
// 获取文章列表
import apiClient from '@/api/client'

const fetchPosts = async () => {
  const response = await apiClient.get('/posts', {
    params: {
      page: 1,
      pageSize: 10,
      category: 'blog',
      draft: false,
    },
  })
  return response.data
}

// 创建文章
const createPost = async (postData: CreatePostDto) => {
  const response = await apiClient.post('/posts', postData)
  return response.data
}

// 更新文章
const updatePost = async (slug: string, postData: UpdatePostDto) => {
  const response = await apiClient.put(`/posts/${slug}`, postData)
  return response.data
}

// 删除文章
const deletePost = async (slug: string) => {
  const response = await apiClient.delete(`/posts/${slug}`)
  return response.data
}
```

---

## 11. 附录

### 11.1 Mock 数据生成

前端当前使用的假数据位于 `src/stores/content.ts`，包含：

- 17 篇博客文章
- 8 个项目
- 9 条生活记录

### 11.2 联调检查清单

前后端联调时需要检查的项目：

- [ ] 登录功能是否正常
- [ ] Token 刷新机制是否工作
- [ ] 文章列表分页是否正确
- [ ] 搜索功能是否返回正确结果
- [ ] 创建/更新/删除文章是否成功
- [ ] 草稿/文章状态切换是否正确
- [ ] 浏览统计是否正确记录
- [ ] 点赞功能是否正常
- [ ] 相关推荐是否准确
- [ ] 错误处理是否友好

### 11.3 性能优化建议

1. **数据库索引**：确保所有常用查询字段都有索引
2. **Redis 缓存**：
   - 缓存热门文章列表
   - 缓存标签统计
   - 缓存浏览统计
3. **Elasticsearch**：
   - 全文搜索性能优化
   - 中文分词配置
4. **分页优化**：
   - 使用游标分页替代偏移量分页
   - 避免深分页性能问题

---

## 12. 联系方式

如有疑问，请联系：

- **项目地址**: https://github.com/your-username/nano-banana
- **文档仓库**: https://github.com/your-username/nano-banana-docs
- **Issue 跟踪**: https://github.com/your-username/nano-banana/issues

---

**文档结束** 🎉
