# Django 博客后端 - 调研发现

## 前端分析结果

### 项目结构
```
frontend/
├── src/
│   ├── components/      # UI 组件
│   │   ├── content/     # 内容相关 (MarkdownRenderer, TableOfContents)
│   │   ├── home/        # 首页组件
│   │   ├── search/      # 搜索组件
│   │   ├── comments/    # 评论 (GiscusComments)
│   │   ├── ai/          # AI 助手
│   │   └── effects/     # 特效组件
│   ├── layouts/         # 布局组件
│   ├── pages/           # 页面组件
│   │   ├── admin/       # 管理后台
│   │   ├── blog/        # 博客页面
│   │   ├── projects/    # 项目页面
│   │   └── life/        # 生活页面
│   ├── stores/          # Pinia 状态管理
│   │   ├── content.ts   # 内容数据
│   │   ├── admin.ts     # 管理员认证
│   │   ├── search.ts    # 搜索状态
│   │   └── aiChat.ts    # AI 聊天
│   ├── types/           # TypeScript 类型定义
│   │   ├── content.ts   # 内容类型
│   │   └── search.ts    # 搜索类型
│   └── utils/           # 工具函数
│       ├── contentLoader.ts  # 内容加载
│       ├── markdown.ts       # Markdown 处理
│       └── anthropic.ts      # AI API
```

### 数据模型发现

#### PostSummary (文章摘要)
```typescript
{
  slug: string              // URL 友好标识
  title: string             // 标题
  description: string       // 描述
  date: string              // ISO 日期
  tags: string[]            // 标签数组
  category: 'blog' | 'projects' | 'life' | 'notes'
  locale: 'zh' | 'en'       // 语言
  readingTime: number       // 阅读时间(分钟)
  featured: boolean         // 是否精选
  draft: boolean            // 是否草稿
}
```

#### Post (完整文章)
```typescript
{
  slug: string
  content: string           // Markdown 内容
  frontmatter: PostFrontmatter
}
```

#### ProjectPost (项目扩展)
```typescript
{
  stars: number             // GitHub stars
  forks: number             // GitHub forks
  repo: string              // 仓库地址
  demo: string              | null  // 演示地址
  techStack: string[]       // 技术栈
  status: 'active' | 'maintenance' | 'archived'
}
```

#### LifePost (生活动态扩展)
```typescript
{
  coverImage: string        // 封面图片
}
```

### API 需求分析

#### 1. 内容过滤 API
```typescript
ContentFilter {
  category?: 'blog' | 'projects' | 'life' | 'notes'
  tags?: string[]
  locale?: 'zh' | 'en'
  draft?: boolean
  featured?: boolean
  search?: string
  sortBy?: 'date' | 'popularity' | 'readingTime' | 'title'
  sortOrder?: 'asc' | 'desc'
  dateFrom?: string
  dateTo?: string
}
```

#### 2. 认证需求
- 简单密码登录 (admin/admin)
- 单用户模式
- localStorage 存储登录状态

#### 3. 搜索需求
- 全文搜索 (标题、描述、标签)
- 搜索历史 (最多 10 条)
- 搜索建议
- 键盘导航支持

#### 4. 管理后台需求
- 文章列表 (查看、编辑、删除)
- 创建新文章
- 草稿管理

---

## 后端技术调研

### Django vs Flask vs FastAPI

| 框架 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| Django | 功能完整、ORM 强大、Admin 后台 | 较重 | ✅ 内容管理系统 |
| Flask | 轻量、灵活 | 需要自己组装 | 小型 API |
| FastAPI | 高性能、自动文档 | 生态较新 | 高并发 API |

**结论**: 选择 Django，适合博客 CMS 场景

### 数据库选型

| 数据库 | 用途 | 理由 |
|--------|------|------|
| MySQL | 主数据库 | 成熟稳定、事务支持 |
| Redis | 缓存/会话 | 高性能、支持多种数据结构 |
| Elasticsearch | 全文搜索 | 专业的搜索引擎 |

### 缓存策略

#### 缓存层级
1. **Redis 缓存** (L1):
   - 热门文章
   - 文章详情
   - 搜索结果
   - 分类/标签列表

2. **数据库查询优化** (L2):
   - select_related (ForeignKey)
   - prefetch_related (ManyToMany)

#### 缓存失效策略
- 创建/更新文章 → 清除相关缓存
- 删除文章 → 清除缓存 + ES 索引
- 定时预热热门数据

### 异步任务场景

| 任务 | 异步原因 | 优先级 |
|------|----------|--------|
| 阅读量更新 | 避免频繁写库 | 低 |
| ES 索引同步 | 不影响主流程 | 中 |
| 统计数据生成 | 计算密集 | 中 |
| 缓存刷新 | 批量处理 | 低 |
| 邮件发送 | 耗时操作 | 低 |

---

## Elasticsearch 索引设计

### Article Index

```json
{
  "mappings": {
    "properties": {
      "id": { "type": "integer" },
      "title": { "type": "text", "analyzer": "ik_max_word" },
      "description": { "type": "text", "analyzer": "ik_max_word" },
      "content": { "type": "text", "analyzer": "ik_max_word" },
      "tags": { "type": "keyword" },
      "category": { "type": "keyword" },
      "locale": { "type": "keyword" },
      "date": { "type": "date" },
      "view_count": { "type": "integer" },
      "featured": { "type": "boolean" }
    }
  },
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "ik_max_word": {
          "type": "custom",
          "tokenizer": "ik_max_word"
        }
      }
    }
  }
}
```

### 分词器选择
- 中文: IK Analysis Plugin (ik_max_word)
- 英文: Standard Analyzer

---

## 数据库表设计

### users 表
```sql
CREATE TABLE users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE,
    password VARCHAR(128) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_staff BOOLEAN DEFAULT FALSE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);
```

### articles 表
```sql
CREATE TABLE articles (
    id INT PRIMARY KEY AUTO_INCREMENT,
    slug VARCHAR(200) UNIQUE NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    content LONGTEXT,
    author_id INT,
    category_id INT,
    locale VARCHAR(2) DEFAULT 'zh',
    reading_time INT DEFAULT 0,
    featured BOOLEAN DEFAULT FALSE,
    draft BOOLEAN DEFAULT FALSE,
    view_count INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    published_at DATETIME,
    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (category_id) REFERENCES categories(id),
    INDEX idx_slug (slug),
    INDEX idx_category (category_id),
    INDEX idx_draft_featured (draft, featured),
    INDEX idx_published (published_at)
);
```

### categories 表
```sql
CREATE TABLE categories (
    id INT PRIMARY KEY AUTO_INCREMENT,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    sort_order INT DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### tags 表
```sql
CREATE TABLE tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### article_tags 表 (多对多)
```sql
CREATE TABLE article_tags (
    id INT PRIMARY KEY AUTO_INCREMENT,
    article_id INT NOT NULL,
    tag_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
    UNIQUE KEY unique_article_tag (article_id, tag_id)
);
```

### comments 表
```sql
CREATE TABLE comments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    article_id INT NOT NULL,
    author_id INT,
    parent_id INT DEFAULT NULL,
    content TEXT NOT NULL,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES users(id),
    FOREIGN KEY (parent_id) REFERENCES comments(id) ON DELETE CASCADE
);
```

### view_counts 表
```sql
CREATE TABLE view_counts (
    id INT PRIMARY KEY AUTO_INCREMENT,
    article_id INT NOT NULL UNIQUE,
    count INT DEFAULT 0,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (article_id) REFERENCES articles(id) ON DELETE CASCADE
);
```

---

## 统一 API 响应格式

### 成功响应
```json
{
  "code": 200,
  "message": "success",
  "data": { ... }
}
```

### 列表响应 (分页)
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "items": [ ... ],
    "pagination": {
      "page": 1,
      "page_size": 20,
      "total": 100,
      "total_pages": 5
    }
  }
}
```

### 错误响应
```json
{
  "code": 400,
  "message": "Validation error",
  "errors": { ... }
}
```

---

## 安全考虑

### 认证与授权
- JWT Token 认证
- Token 过期时间: 24 小时
- Refresh Token: 7 天

### 权限控制
- 普通用户: 读取公开内容
- 管理员: 完整 CRUD 权限

### 限流策略
- 匿名用户: 100 req/min
- 认证用户: 200 req/min
- 登录接口: 10 req/min

### 数据验证
- 使用 Django Form/Serializer 验证
- SQL 注入防护 (ORM 参数化查询)
- XSS 防护 (模板转义)
- CSRF 保护

---

## 性能优化建议

### 数据库优化
1. 添加适当索引
2. 查询优化 (select_related, prefetch_related)
3. 连接池配置

### 缓存优化
1. Redis 缓存热点数据
2. 缓存预热
3. 合理设置 TTL

### API 优化
1. 分页减少数据量
2. 字段选择 (只返回需要的字段)
3. 压缩响应 (gzip)

---

## 待解决的问题

1. **Giscus 评论集成**: 需要确认如何与后端数据同步
2. **图片存储**: 本地存储 vs OSS (阿里云/七牛)
3. **AI 助手**: 是否需要后端 API 代理
4. **部署方式**: Docker 部署具体配置
5. **监控方案**: 日志收集、性能监控

---

## 参考资料

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [Celery Documentation](https://docs.celeryq.dev/)
- [Elasticsearch Python Client](https://elasticsearch-py.readthedocs.io/)
- [drf-yasg](https://drf-yasg.readthedocs.io/)
