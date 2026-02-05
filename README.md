# 🍌 Nano Banana

> 一个功能完整的全栈个人博客系统，支持文章、项目展示、生活记录和评论系统。

[![Vue](https://img.shields.io/badge/Vue-3.5-4FC08D?logo=vue.js&logoColor=white)
[![Django](https://img.shields.io/badge/Django-5.2-092E20?logo=django&logoColor=white)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.7-3178C6?logo=typescript&logoColor=white)
[![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ 特性

### 📝 内容管理
- **多类型内容支持** - 博客文章、项目展示、生活随笔、快速笔记
- **Markdown 编辑** - 支持实时预览的 Markdown 编辑器
- **富文本内容** - 代码高亮、图片上传、标签分类
- **草稿系统** - 保存草稿，随时发布

### 🔍 强大的搜索
- **Elasticsearch** - 基于 ES 8.17 的全文搜索引擎
- **智能推荐** - 基于标签相似度的相关文章推荐
- **混合存储** - ES 索引 + MySQL 主数据，性能最优

### 👥 用户互动
- **评论系统** - 支持嵌套回复、游客评论
- **点赞功能** - 文章点赞、统计展示
- **阅读统计** - 浏览量、阅读时间统计

### 🎨 现代化界面
- **响应式设计** - 完美适配桌面和移动端
- **深色模式** - 支持明暗主题切换
- **流畅动画** - ScrollReveal 滚动动画效果
- **渐变设计** - 蓝紫渐变色主题

### 🔐 安全性
- **JWT 认证** - 自动刷新 Token，安全可靠
- **频率限制** - API 防滥用保护
- **权限管理** - 基于角色的访问控制
- **CORS 配置** - 生产环境安全配置

---

## 🛠️ 技术栈

### 前端
```
Vue 3.5                - Composition API + <script setup>
TypeScript 5.7         - 类型安全
Vite 6.x                - 构建工具
Tailwind CSS 3.x         - 原子化 CSS
Pinia                   - 状态管理
Vue Router 4.x           - 文件路由 (unplugin-vue-router)
Iconify (Lucide)         - 图标库
vue-i18n                - 国际化
```

### 后端
```
Django 5.2              - Web 框架
Django REST Framework  - API 框架
MySQL 8.0               - 主数据库
Elasticsearch 8.17      - 搜索引擎
Redis                   - 缓存
Celery 5.4              - 异步任务
SimpleJWT               - JWT 认证
```

### DevOps
```
Docker Compose          - 容器编排
Nginx                   - 反向代理
Git                     - 版本控制
```

---

## 📁 项目结构

```
p:\workspace\blog\
├── frontend/                    # Vue 3 前端
│   ├── src/
│   │   ├── api/              # API 客户端和服务
│   │   ├── assets/           # 静态资源
│   │   ├── components/       # 可复用组件
│   │   │   ├── admin/        # 管理后台组件
│   │   │   ├── blog/         # 博客相关组件
│   │   │   ├── comments/     # 评论组件
│   │   │   ├── home/         # 首页组件
│   │   │   ├── projects/     # 项目组件
│   │   │   ├── ui/           # UI 组件
│   │   │   └── ...
│   │   ├── layouts/          # 布局组件
│   │   ├── pages/            # 页面组件（文件路由）
│   │   ├── stores/           # Pinia 状态管理
│   │   ├── utils/            # 工具函数
│   │   ├── types/            # TypeScript 类型定义
│   │   └── locales/          # 国际化文件
│   ├── public/               # 公共静态文件
│   ├── index.html            # 入口 HTML
│   ├── vite.config.ts        # Vite 配置
│   └── tailwind.config.js     # Tailwind 配置
│
├── backend/                     # Django 后端
│   ├── articles/             # 文章应用
│   │   ├── models.py         # 文章模型
│   │   ├── serializers.py    # API 序列化器
│   │   ├── views.py          # API 视图
│   │   ├── signals.py       # 数据同步信号
│   │   └── urls.py          # URL 配置
│   ├── users/                # 用户应用
│   │   ├── models.py         # 用户模型
│   │   ├── serializers.py    # 认证序列化器
│   │   ├── views.py          # 认证视图
│   │   └── urls.py          # URL 配置
│   ├── comments/             # 评论应用
│   ├── categories/           # 分类应用
│   ├── tags/                 # 标签应用
│   ├── stats/                # 统计应用
│   ├── search/               # 搜索应用 (Elasticsearch)
│   ├── config/               # 项目配置
│   │   ├── settings/        # 设置文件
│   │   │   ├── base.py       # 基础配置
│   │   │   ├── development.py
│   │   │   └── production.py
│   │   ├── urls.py          # 主 URL 配置
│   │   └── wsgi.py           # WSGI 配置
│   ├── manage.py             # Django 管理命令
│   └── requirements.txt      # Python 依赖
│
├── .gitignore                 # Git 忽略文件
├── docker-compose.yml         # Docker Compose 配置
└── README.md                 # 项目文档
```

---

## 🚀 快速开始

### 环境要求

- **Node.js** >= 18.x
- **Python** >= 3.11
- **MySQL** >= 8.0
- **Redis** >= 6.x
- **Elasticsearch** >= 8.x

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/你的用户名/blog.git
cd blog
```

#### 2. 后端设置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库和其他服务

# 运行数据库迁移
python manage.py makemigrations
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# 启动开发服务器
python manage.py runserver
```

#### 3. 前端设置

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置 API 地址

# 启动开发服务器
npm run dev
```

#### 4. 使用 Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 访问应用

- **前台**: http://localhost:5173
- **后台管理**: http://localhost:5173/admin
- **API 文档**: http://localhost:8000/api/docs/

---

## 🔧 配置说明

### 环境变量

#### 前端 (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

#### 后端 (.env)
```bash
# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
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

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=10080
```

### 生产环境配置

1. **修改 SECRET_KEY**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **配置 DEBUG=False**
   ```python
   DEBUG = False
   ALLOWED_HOSTS = ['yourdomain.com']
   ```

3. **配置 CORS**
   ```python
   CORS_ALLOWED_ORIGINS = ['https://yourdomain.com']
   ```

4. **静态文件服务**
   ```bash
   python manage.py collectstatic --noinput
   ```

---

## 📚 开发指南

### 前端开发

```bash
# 开发服务器
npm run dev

# 类型检查
npm run type-check

# 构建生产版本
npm run build

# 预览构建
npm run preview
```

### 后端开发

```bash
# 运行服务器
python manage.py runserver

# 创建迁移
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser

# Django Shell
python manage.py shell

# 运行测试
pytest

# 代码检查
flake8
black .
```

### Celery 任务

```bash
# 启动 Celery Worker
celery -A config worker -l info

# 启动 Celery Beat
celery -A config beat -l info

# 查看任务状态
celery -A config inspect active
```

### Elasticsearch 管理

```bash
# 重建索引
python manage.py shell << EOF
from search.models import ArticleDocument
ArticleDocument._index.delete()
ArticleDocument._index.create()
ArticleDocument.init()
ArticleDocument().update(compare=False)
EOF
```

---

## 📦 API 文档

### 认证接口

```bash
# 登录
POST /api/auth/login/
Body: { "username": "admin", "password": "yourpassword" }

# 刷新 Token
POST /api/auth/refresh/
Body: { "refresh": "your_refresh_token" }
```

### 文章接口

```bash
# 获取文章列表
GET /api/articles/?category=blog&page=1&page_size=10

# 获取文章详情
GET /api/articles/{slug}/

# 创建文章
POST /api/articles/
Headers: Authorization: Bearer {access_token}
Body: {
  "title": "文章标题",
  "content": "文章内容",
  "category_id": 1,
  "tag_ids": [1, 2],
  ...
}
```

更多 API 详情请访问：http://localhost:8000/api/docs/

---

## 🎨 功能预览

### 首页
- ✅ Hero 区域展示
- ✅ 内容统计卡片（博客、项目、生活数量）
- ✅ 精选文章展示
- ✅ 最新文章列表

### 文章详情
- ✅ 阅读进度条
- ✅ Markdown 渲染
- ✅ 代码高亮
- ✅ 相关文章推荐
- ✅ 评论系统

### 项目展示
- ✅ 项目卡片展示
- ✅ 技术栈标签
- ✅ GitHub 链接
- ✅ 在线演示链接

### 后台管理
- ✅ 文章管理（增删改查）
- ✅ 项目管理
- ✅ 生活记录管理
- ✅ 评论审核
- ✅ 统计分析

---

## 🧪 测试

```bash
# 前端测试
cd frontend
npm run test

# 后端测试
cd backend
pytest

# 测试覆盖率
pytest --cov=. --cov-report=html
```

---

## 📝 更新日志

### v1.0.0 (2024-02-06)

#### 新增
- ✅ ES + MySQL 混合存储架构
- ✅ JWT Token 认证 + 自动刷新
- ✅ 评论系统（嵌套回复、审核）
- ✅ 全文搜索（Elasticsearch）
- ✅ 后台管理系统
- ✅ 响应式设计 + 深色模式

#### 优化
- ✅ N+1 数据库查询优化
- ✅ 评论频率限制
- ✅ 统一日志系统
- ✅ 代码质量提升

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 开发流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范

- **前端**: 遵循 ESLint 配置
- **后端**: 遵循 PEP 8，使用 black 格式化
- **提交信息**: 使用清晰的提交信息

---

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 👨‍💻 作者

**Nano Banana** - 一个热爱技术的全栈开发者

- 📧 Email: your-email@example.com
- 🌐 Website: [yourwebsite.com](https://yourwebsite.com)
- 💻 GitHub: [@yourusername](https://github.com/yourusername)

---

## 🙏 致谢

感谢以下开源项目：

- [Vue.js](https://vuejs.org/)
- [Django](https://www.djangoproject.com/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Lucide Icons](https://lucide.dev/)
- [Elasticsearch](https://www.elastic.co/)

---

## 📞 联系方式

- **问题反馈**: [GitHub Issues](https://github.com/你的用户名/blog/issues)
- **功能建议**: 欢迎提交 Issue 或 PR
- **商务合作**: your-email@example.com

---

## 🌟 Star History

如果这个项目对你有帮助，请给个 Star ⭐️

![Star History Chart](https://api.star-history.com/svg?repos=你的用户名/blog&type=Date)

---

<div align="center">

**Made with ❤️ by Nano Banana**

**[⬆ 返回顶部](#)**

</div>
