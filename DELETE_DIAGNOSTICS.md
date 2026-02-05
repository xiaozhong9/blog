# 删除文章问题诊断指南

## 问题现象
删除文章后刷新页面，数据还在。

## 已确认正常的部分
✅ 后端删除功能正常（通过 Python 测试脚本验证）
✅ MySQL 删除成功
✅ ES 索引同步删除成功

## 需要检查的前端问题

### 1. 打开浏览器开发者工具

**Chrome/Edge**: 按 F12
**Firefox**: 按 F12

### 2. 切换到 Network 标签页

1. 点击 Network 标签
2. 勾选 "Preserve log"（保留日志）
3. 准备监控网络请求

### 3. 执行删除操作

1. 访问 `http://localhost:5173/admin/posts`
2. 点击任意文章的删除按钮
3. 确认删除

### 4. 检查 Network 请求

应该看到以下请求序列：

#### 请求 1: DELETE 请求
```
DELETE /api/articles/{slug}/
Status: 200 OK
Response: { "code": 200, "message": "删除成功", "data": null }
```

**如果看到 401/403**: 认证或权限问题
- 检查 localStorage 中是否有 `access_token`
- 尝试重新登录

**如果看到 404**: 文章不存在或 slug 错误
- 检查传递的 slug 是否正确

#### 请求 2: GET 请求（重新加载）
```
GET /api/articles/?category=blog&page=1&page_size=100
Status: 200 OK
```

检查响应的 `data.results` 数组中是否包含被删除的文章。

### 5. 检查 Console 标签页

查看是否有 JavaScript 错误：
- 红色的错误信息
- 未捕获的异常

### 6. 检查 Application 标签页

1. 切换到 Application 标签
2. 左侧选择 "Local Storage"
3. 检查是否有 `access_token` 和 `refresh_token`
4. 如果没有，说明未登录或 token 已过期

## 常见问题和解决方案

### 问题 1: 401 Unauthorized
**原因**: Token 过期或无效
**解决**:
1. 清除 localStorage
2. 重新登录

### 问题 2: 403 Forbidden
**原因**: 权限不足
**解决**:
- 确认当前用户是管理员
- 确认是文章作者或管理员

### 问题 3: 删除成功但列表不刷新
**原因**: 组件缓存或状态更新失败
**解决**:
1. 强制刷新页面（Ctrl+F5）
2. 清除浏览器缓存

### 问题 4: ES 和 MySQL 不同步
**原因**: ES 索引未更新
**解决**: 已通过重建索引修复

## 手动测试步骤

### 使用浏览器控制台测试

1. 打开 `http://localhost:5173/admin/posts`
2. 打开开发者工具（F12）
3. 在 Console 中执行以下代码：

```javascript
// 检查 token
console.log('Token:', localStorage.getItem('access_token'))

// 检查 store 数据
console.log('Posts:', window.$pinia?.state?.adminContent?.posts?.length)
```

### 使用 cURL 测试删除 API

```bash
# 1. 登录获取 token
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 2. 使用返回的 token 删除文章
curl -X DELETE http://localhost:8000/api/articles/article-20/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# 3. 查询文章列表
curl "http://localhost:8000/api/articles/?category=blog&page_size=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 预期结果

删除成功后应该看到：
1. 成功通知："文章已删除"
2. 文章从列表中消失
3. 刷新页面后文章仍然不在列表中

## 如果问题仍然存在

请提供以下信息：
1. Network 标签页中 DELETE 请求的完整响应
2. Console 标签页中的错误信息
3. Application 标签页中 Local Storage 的截图
