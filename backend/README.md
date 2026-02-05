# Nano Banana Blog - Django Backend

Nano Banana 博客系统的 Django REST Framework 后端。

## 项目概述

这是一个功能完整的博客后端系统，支持：
- ✅ JWT 认证系统
- ✅ RESTful API
- ✅ MySQL 数据库
- ✅ Redis 缓存
- ✅ Elasticsearch 全文搜索
- ✅ Celery 异步任务
- ✅ Swagger API 文档

## 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.11+ | 编程语言 |
| Django | 5.2.9 | Web 框架 |
| DRF | 3.16.0 | REST API 框架 |
| MySQL | 8.0 | 主数据库 |
| Redis | 7.x | 缓存/消息队列 |
| Elasticsearch | 8.17.2 | 全文搜索 |
| Celery | 5.4.0 | 异步任务 |

## 项目结构

```
backend/
├── config/                 # 主配置目录
│   ├── settings/          # 模块化配置
│   │   ├── base.py       # 基础配置
│   │   ├── dev.py        # 开发配置
│   │   └── prod.py       # 生产配置
│   ├── urls.py           # 主 URL 配置
│   ├── celery.py         # Celery 配置
│   └── exceptions.py     # 异常处理
│
├── users/                 # 用户模块 ✅
│   ├── models.py         # 用户模型
│   ├── serializers/      # 序列化器
│   ├── views/            # 视图
│   └── urls.py           # URL 配置
│
├── articles/              # 文章模块 ✅
│   ├── models.py         # 文章、阅读记录、版本控制
│   └── urls.py           # URL 配置
│
├── categories/            # 分类模块 ✅
│   ├── models.py         # 分类模型
│   └── urls.py           # URL 配置
│
├── tags/                  # 标签模块 ✅
│   ├── models.py         # 标签模型
│   └── urls.py           # URL 配置
│
├── comments/              # 评论模块 ✅
│   ├── models.py         # 评论模型 (支持 Giscus)
│   └── urls.py           # URL 配置
│
├── search/                # 搜索模块 ✅
│   ├── models.py         # Elasticsearch 文档
│   ├── views.py          # 搜索视图
│   └── urls.py           # URL 配置
│
├── stats/                 # 统计模块 ✅
│   ├── models.py         # 统计模型
│   └── urls.py           # URL 配置
│
├── manage.py              # Django 管理脚本
├── requirements.txt       # 依赖包
├── .env                   # 环境变量
├── Dockerfile             # Docker 配置
└── docker-compose.yml     # Docker Compose 配置
```

## 快速开始

### 1. 环境要求

- Python 3.11+
- MySQL 8.0
- Redis 7.x
- Elasticsearch 8.x (可选)

### 2. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 到 `.env` 并修改配置：

```bash
cp .env.example .env
```

主要配置项：
```env
SECRET_KEY=your-secret-key
DEBUG=True

# MySQL
DB_NAME=nano_banana_db
DB_USER=root
DB_PASSWORD=admin
DB_HOST=localhost
DB_PORT=3306

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Elasticsearch
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
```

### 4. 数据库迁移

```bash
# 创建数据库
mysql -u root -p -e "CREATE DATABASE nano_banana_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# 执行迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 5. 启动服务

```bash
# 启动 Django 开发服务器
python manage.py runserver

# 启动 Celery Worker (新终端)
celery -A config worker -l info

# 启动 Celery Beat (新终端)
celery -A config beat -l info
```

### 6. 访问服务

- **API 文档 (Swagger)**: http://localhost:8000/swagger/
- **API 文档 (ReDoc)**: http://localhost:8000/redoc/
- **Django Admin**: http://localhost:8000/admin/

## Docker 部署

使用 Docker Compose 一键启动所有服务：

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

服务列表：
- `backend` - Django 后端 (端口 8000)
- `celery_worker` - Celery 任务队列
- `celery_beat` - Celery 定时任务
- `mysql` - MySQL 数据库 (端口 3306)
- `redis` - Redis 缓存 (端口 6379)
- `elasticsearch` - Elasticsearch (端口 9200)
- `flower` - Celery 监控 (端口 5555)

## API 端点

### 认证 API (`/api/auth/`)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | `/register/` | 用户注册 |
| POST | `/login/` | 用户登录 |
| POST | `/logout/` | 用户登出 |
| GET | `/me/` | 获取当前用户信息 |
| POST | `/refresh/` | 刷新 Token |
| POST | `/users/{id}/change-password/` | 修改密码 |

### 文章 API (`/api/articles/`)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | 文章列表 (分页/过滤/排序) |
| GET | `/{slug}/` | 文章详情 |
| POST | `/` | 创建文章 |
| PUT | `/{slug}/` | 更新文章 |
| DELETE | `/{slug}/` | 删除文章 |
| GET | `/featured/` | 精选文章 |
| GET | `/popular/` | 热门文章 |

### 分类 API (`/api/categories/`)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | 分类列表 |
| POST | `/` | 创建分类 |
| GET | `/{slug}/` | 分类详情 |
| PUT | `/{slug}/` | 更新分类 |
| DELETE | `/{slug}/` | 删除分类 |

### 标签 API (`/api/tags/`)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | 标签列表 |
| POST | `/` | 创建标签 |
| GET | `/{slug}/` | 标签详情 |
| PUT | `/{slug}/` | 更新标签 |
| DELETE | `/{slug}/` | 删除标签 |

### 搜索 API (`/api/search/`)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | 全文搜索 |
| GET | `/suggest/` | 搜索建议 |

### 统计 API (`/api/stats/`)

| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/overview` | 总览统计 |
| GET | `/popular/articles` | 热门文章 |

## 数据模型

### 用户 (User)
- 扩展 Django AbstractUser
- 支持角色系统 (admin/editor/user)
- 头像、简介、个人网站

### 文章 (Article)
- 标题、内容、描述
- 分类、标签 (多对多)
- Markdown 支持
- 阅读时间自动计算
- 版本控制
- 项目专属字段 (stars/forks/repo/demo)

### 分类 (Category)
- 类型 (blog/projects/life/notes)
- 图标、排序
- SEO 关键词

### 标签 (Tag)
- 名称、描述
- 颜色
- 统计

### 评论 (Comment)
- 支持 Giscus 集成
- 嵌套回复
- Markdown 支持

### 统计 (Stats)
- 每日统计
- 文章统计
- 用户行为记录

## 开发指南

### 代码风格

```bash
# 代码格式化
black .

# 代码检查
flake8
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest users/tests/

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 添加新 API

1. 在 `models.py` 中定义数据模型
2. 在 `serializers.py` 中创建序列化器
3. 在 `views.py` 中创建视图
4. 在 `urls.py` 中注册路由
5. 添加 Swagger 文档注释

## 配置说明

### JWT 认证配置

- Access Token 有效期：60 分钟
- Refresh Token 有效期：7 天
- 支持 Token 刷新和黑名单

### Redis 缓存配置

缓存策略：
- 文章详情：1 小时
- 热门文章：30 分钟
- 搜索结果：15 分钟
- 分类/标签列表：1 小时

### Elasticsearch 配置

- 索引名称：`banana_articles`
- 分词器：IK Analysis Plugin
- 支持中文全文搜索
- 高亮显示
- 搜索建议

## 常见问题

### 1. 数据库连接失败

检查 MySQL 服务是否启动，配置是否正确。

### 2. Redis 连接失败

检查 Redis 服务是否启动。

### 3. Elasticsearch 连接失败

检查 Elasticsearch 服务是否启动，IK 分词插件是否安装。

### 4. Celery 任务不执行

检查 Celery Worker 是否启动，查看日志。

## 贡献指南

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License

## 联系方式

- 项目地址：https://github.com/yourname/nano-banana
- 邮箱：admin@nanobanana.dev

---

**开发进度**: 50% (核心功能已实现，部分 API 待完善)
