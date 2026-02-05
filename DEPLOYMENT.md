# Nano Banana Blog 部署指南

本文档介绍如何将 Nano Banana Blog 项目部署到生产服务器。

## 目录结构

```
blog/
├── backend/                 # Django 后端
│   ├── media/              # 媒体文件目录（图片等）
│   │   └── uploads/
│   │       └── images/
│   │           └── YYYY/MM/DD/  # 按日期组织的图片
│   ├── staticfiles/        # 收集的静态文件
│   └── manage.py
└── frontend/               # Vue 前端
    └── dist/               # 构建产物
```

## 图片存储配置

### 当前配置

图片上传后存储路径：`media/uploads/images/YYYY/MM/DD/`

- **存储根目录**: `MEDIA_ROOT = BASE_DIR / 'media'`
- **访问 URL**: `MEDIA_URL = '/media/'`
- **上传子目录**: `uploads/images/YYYY/MM/DD/`
- **完整路径**: `media/uploads/images/2025/02/04/xxxxxxxxxxxx.jpg`

### 开发环境

在开发环境中，Django 会自动提供媒体文件服务（通过 `config/urls.py`）：

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

访问 URL 示例：
- 开发环境: `http://localhost:8000/media/uploads/images/2025/02/04/abc123.jpg`

### 生产环境

在生产环境中，需要使用 Web 服务器（如 Nginx）来提供媒体文件服务。

## Nginx 配置示例

创建 Nginx 配置文件 `/etc/nginx/sites-available/nano-banana-blog`：

```nginx
# 上游服务器配置
upstream backend {
    server 127.0.0.1:8000;
}

# HTTP 服务器（建议配置 SSL）
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 10M;  # 允许上传最大 10MB 文件

    # 前端静态文件
    location / {
        root /path/to/blog/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Django Admin
    location /admin/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 媒体文件（图片等）
    location /media/ {
        alias /path/to/blog/backend/media/;
        expires 30d;  # 浏览器缓存 30 天
        add_header Cache-Control "public, immutable";
    }

    # 静态文件（CSS, JS 等）
    location /static/ {
        alias /path/to/blog/backend/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

### 启用配置

```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/nano-banana-blog /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

## 环境变量配置

确保 `.env` 文件配置正确：

```bash
# Django 基础配置
SECRET_KEY=your-production-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# 数据库配置
DB_ENGINE=django.db.backends.mysql
DB_NAME=nano_banana_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# 媒体文件配置
MEDIA_URL=/media/
MEDIA_ROOT=media

# CORS 配置（生产环境设置实际域名）
CORS_ALLOWED_ORIGINS=https://your-domain.com,https://www.your-domain.com
```

## 部署步骤

### 1. 准备服务器环境

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.10+
sudo apt install python3.10 python3.10-venv python3-pip -y

# 安装 MySQL
sudo apt install mysql-server -y
sudo mysql_secure_installation

# 安装 Redis
sudo apt install redis-server -y

# 安装 Nginx
sudo apt install nginx -y

# 安装 Node.js 18+
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install nodejs -y
```

### 2. 部署后端

```bash
# 进入项目目录
cd /path/to/blog/backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 执行数据库迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 创建超级用户（可选）
python manage.py createsuperuser

# 使用 Gunicorn 运行（推荐）
pip install gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000
```

### 3. 使用 Systemd 管理后端服务

创建服务文件 `/etc/systemd/system/nano-banana-backend.service`：

```ini
[Unit]
Description=Nano Banana Blog Django Backend
After=network.target mysql.service redis.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/path/to/blog/backend
Environment="PATH=/path/to/blog/backend/venv/bin"
ExecStart=/path/to/blog/backend/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/path/to/blog/backend/gunicorn.sock \
          config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl start nano-banana-backend
sudo systemctl enable nano-banana-backend
sudo systemctl status nano-banana-backend
```

### 4. 部署前端

```bash
# 进入前端目录
cd /path/to/blog/frontend

# 安装依赖
npm install

# 构建生产版本
npm run build

# dist 目录包含了构建产物，配置 Nginx 指向此目录
```

### 5. 配置 Celery（可选）

如果需要使用异步任务和定时任务：

```bash
# 启动 Celery Worker
celery -A config worker -l info

# 启动 Celery Beat
celery -A config beat -l info
```

创建 Systemd 服务管理 Celery：

`/etc/systemd/system/nano-banana-celery.service`:

```ini
[Unit]
Description=Nano Banana Blog Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/blog/backend
Environment="PATH=/path/to/blog/backend/venv/bin"
ExecStart=/path/to/blog/backend/venv/bin/celery -A config worker \
          --pidfile=/var/run/celery/worker.pid \
          --logfile=/var/log/celery/worker.log \
          --loglevel=INFO
Restart=always

[Install]
WantedBy=multi-user.target
```

`/etc/systemd/system/nano-banana-celerybeat.service`:

```ini
[Unit]
Description=Nano Banana Blog Celery Beat
After=network.target redis.service

[Service]
Type=forking
User=www-data
Group=www-data
WorkingDirectory=/path/to/blog/backend
Environment="PATH=/path/to/blog/backend/venv/bin"
ExecStart=/path/to/blog/backend/venv/bin/celery -A config beat \
          --pidfile=/var/run/celery/beat.pid \
          --logfile=/var/log/celery/beat.log \
          --loglevel=INFO \
          --scheduler django_celery_beat.schedulers:DatabaseScheduler
Restart=always

[Install]
WantedBy=multi-user.target
```

## 安全建议

1. **配置防火墙**
   ```bash
   sudo ufw allow 22    # SSH
   sudo ufw allow 80    # HTTP
   sudo ufw allow 443   # HTTPS
   sudo ufw enable
   ```

2. **配置 SSL/TLS（HTTPS）**

   使用 Let's Encrypt 免费证书：
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your-domain.com
   ```

3. **设置文件权限**
   ```bash
   sudo chown -R www-data:www-data /path/to/blog/backend/media
   sudo chmod -R 755 /path/to/blog/backend/media
   ```

4. **定期备份数据库和媒体文件**
   ```bash
   # 备份数据库
   mysqldump -u root -p nano_banana_db > backup_$(date +%Y%m%d).sql

   # 备份媒体文件
   tar -czf media_backup_$(date +%Y%m%d).tar.gz backend/media/
   ```

## 监控和日志

- **Django 日志**: `backend/logs/`
- **Nginx 日志**: `/var/log/nginx/`
- **Celery 日志**: `/var/log/celery/`

## 常见问题

### 图片上传失败

1. 检查 `MEDIA_ROOT` 目录是否存在且有写权限
2. 检查 Nginx 的 `client_max_body_size` 配置
3. 检查 Django 的 `DATA_UPLOAD_MAX_MEMORY_SIZE` 设置

### 静态文件 404

1. 确保运行了 `python manage.py collectstatic`
2. 检查 Nginx 的 `alias` 路径是否正确

### CORS 错误

1. 检查 `.env` 中的 `CORS_ALLOWED_ORIGINS` 配置
2. 确保前端和后端的域名配置正确
