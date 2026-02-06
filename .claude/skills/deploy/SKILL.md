---
name: deploy
description: Nano Banana 博客系统的 Docker 部署和发布流程
allowed_tools: ["Read", "Write", "Edit", "Bash", "Glob"]
---

# Nano Banana 博客 - Docker 部署工作流

你负责 Nano Banana 博客系统的 Docker 部署和发布。

## 部署架构

```
┌─────────────────────────────────────────────┐
│              docker-compose.yml             │
├─────────────────────────────────────────────┤
│  backend          # Django 后端 (端口 8000)  │
│  celery_worker    # Celery 任务队列          │
│  celery_beat      # Celery 定时任务          │
│  mysql            # MySQL 数据库 (端口 3306) │
│  redis            # Redis 缓存 (端口 6379)   │
│  elasticsearch    # Elasticsearch (端口 9200)│
│  flower           # Celery 监控 (端口 5555)  │
└─────────────────────────────────────────────┘
```

## 工作流程

### 第一步：部署前检查

1. **代码检查**
   - [ ] 所有功能已测试
   - [ ] 无调试代码遗留
   - [ ] 环境变量已配置
   - [ ] 数据库迁移文件已准备

2. **环境检查**
   ```bash
   # 检查 Docker
   docker --version
   docker-compose --version

   # 检查端口占用（Windows）
   netstat -ano | findstr "8000"
   netstat -ano | findstr "3306"
   netstat -ano | findstr "6379"
   ```

3. **配置检查**
   - [ ] `p:\workspace\blog\.env` 文件已配置
   - [ ] `p:\workspace\blog\docker-compose.yml` 存在
   - [ ] `p:\workspace\blog\frontend\Dockerfile` 存在
   - [ ] `p:\workspace\blog\backend\Dockerfile` 存在

### 第二步：构建镜像

4. **前端构建**
   ```bash
   cd p:/workspace/blog/frontend
   npm run build
   ```

5. **后端构建**
   - Dockerfile 会自动处理

### 第三步：Docker 部署

6. **启动所有服务**
   ```bash
   cd p:/workspace/blog
   docker-compose up -d
   ```

7. **查看日志**
   ```bash
   # 查看所有日志
   docker-compose logs -f

   # 查看特定服务
   docker-compose logs -f backend
   docker-compose logs -f mysql
   ```

8. **验证服务状态**
   ```bash
   # 查看运行的容器
   docker-compose ps

   # 检查健康状态
   docker-compose ps
   ```

### 第四步：初始化

9. **数据库迁移**
   ```bash
   cd p:/workspace/blog
   # 进入后端容器
   docker-compose exec backend python manage.py migrate

   # 创建超级用户
   docker-compose exec backend python manage.py createsuperuser
   ```

10. **验证服务**
    - 前端：http://localhost:5173
    - 后端 API：http://localhost:8000/api
    - Django Admin：http://localhost:8000/admin
    - Flower：http://localhost:5555

### 第五步：部署后验证

11. **功能测试**
    - [ ] 前端页面加载正常
    - [ ] API 请求正常
    - [ ] 数据库连接正常
    - [ ] Redis 缓存正常
    - [ ] Elasticsearch 连接正常（如已配置）

12. **性能检查**
    ```bash
    # 检查资源使用
    docker stats

    # 检查日志错误
    docker-compose logs | grep -i error
    ```

## 常见问题排查

### 容器启动失败

1. **查看日志**
   ```bash
   docker-compose logs [service_name]
   ```

2. **常见原因**
   - 端口被占用：修改 `docker-compose.yml` 中的端口映射
   - 环境变量缺失：检查 `.env` 文件
   - 数据库连接失败：等待 MySQL 完全启动

### 数据库问题

3. **重置数据库**
   ```bash
   # 停止服务
   cd p:/workspace/blog
   docker-compose down

   # 删除数据卷
   docker volume rm blog_mysql_data

   # 重新启动
   docker-compose up -d

   # 运行迁移
   docker-compose exec backend python manage.py migrate
   ```

### 性能优化

4. **资源限制**
   在 `docker-compose.yml` 中添加：
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '1'
             memory: 1G
   ```

## 项目特定路径

**项目根目录**：`p:\workspace\blog`
**前端目录**：`p:\workspace\blog\frontend`
**后端目录**：`p:\workspace\blog\backend`
**Docker Compose**：`p:\workspace\blog\docker-compose.yml`
**环境变量**：`p:\workspace\blog\.env`

## 维护命令

```bash
cd p:/workspace/blog

# 停止服务
docker-compose down

# 停止并删除数据卷
docker-compose down -v

# 重启服务
docker-compose restart

# 查看资源使用
docker stats

# 清理未使用的镜像
docker image prune

# 查看容器日志
docker-compose logs -f --tail=100 [service]
```

## 输出示例

```markdown
## 🚀 部署完成

**部署环境**：[开发/生产]

**服务状态**：
- ✅ backend (端口 8000)
- ✅ mysql (端口 3306)
- ✅ redis (端口 6379)
- ✅ elasticsearch (端口 9200)
- ✅ celery_worker
- ✅ celery_beat
- ✅ flower (端口 5555)

**访问地址**：
- 前端：http://localhost:5173
- API：http://localhost:8000/api
- Admin：http://localhost:8000/admin
- Flower：http://localhost:5555

**数据迁移**：✅ 完成
**超级用户**：✅ 已创建

**注意事项**：
- [ ] 生产环境需配置 HTTPS
- [ ] 定期备份数据库
- [ ] 监控日志和性能
```

## 注意事项

- ⚠️ 部署前先备份重要数据
- ⚠️ 生产环境使用强密码
- ⚠️ 定期更新依赖包
- ⚠️ 监控日志和性能
- ⚠️ 设置日志轮转
