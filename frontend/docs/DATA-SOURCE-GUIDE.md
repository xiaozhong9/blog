# 数据源切换指南

## 📚 概述

Nano Banana 前端支持两种数据源：
1. **Mock 数据** - 用于前端开发和演示
2. **API 数据** - 连接真实的后端服务

## 🔧 数据源说明

### Store 文件

| 文件 | 用途 | 状态 |
|------|------|------|
| `src/stores/content.ts` | Mock 数据存储 | ✅ 当前使用 |
| `src/stores/content.api.ts` | API 集成存储 | 📦 待后端完成 |

### 当前配置

**所有页面已切换到使用 Mock 数据** ✅

## 🚀 使用 Mock 数据（默认）

### 优点
- ✅ 无需后端即可运行
- ✅ 开发速度快
- ✅ 数据稳定可控
- ✅ 适合前端开发和演示

### 使用的文件
```typescript
// 所有页面都使用这个 store
import { useContentStore } from '@/stores/content'
```

### Mock 数据位置
所有 mock 数据定义在：`src/stores/content.ts` 文件中

包含的数据：
- 博客文章：17 篇
- 项目展示：6 个
- 生活记录：8 篇
- 总计：31 条内容

## 🔌 切换到 API 数据（需要后端）

### 前提条件
- ✅ 后端 API 已部署
- ✅ API 端点已实现（参考 `docs/api/README.md`）
- ✅ 已配置 `.env` 文件

### 切换步骤

#### 1. 配置 API 地址

在 `.env` 文件中配置：
```bash
VITE_API_BASE_URL=http://localhost:8000/api
```

#### 2. 修改页面导入

将页面中的导入从：
```typescript
import { useContentStore } from '@/stores/content'
```

改为：
```typescript
import { useContentStore } from '@/stores/content.api'
```

#### 3. 需要修改的文件列表

**页面文件：**
- `src/pages/index.page.vue`
- `src/pages/blog/index.page.vue`
- `src/pages/blog/[slug].page.vue`
- `src/pages/projects/index.page.vue`
- `src/pages/projects/[slug].page.vue`
- `src/pages/life/index.page.vue`
- `src/pages/life/[slug].page.vue`

**组件文件：**
- `src/components/home/FeaturedSection.vue`
- `src/components/home/LatestPostsSection.vue`
- `src/components/blog/RelatedPosts.vue`
- `src/components/dev/DebugPanel.vue`

### 快速切换脚本

您可以批量替换导入语句：
```bash
# 切换到 API 模式
find src -name "*.vue" -type f -exec sed -i "s|@/stores/content|@/stores/content.api|g" {} +

# 切换回 Mock 模式
find src -name "*.vue" -type f -exec sed -i "s|@/stores/content.api|@/stores/content|g" {} +
```

Windows PowerShell：
```powershell
# 切换到 API 模式
Get-ChildItem -Path src -Recurse -Filter "*.vue" | ForEach-Object {
  (Get-Content $_.FullName) -replace [regex]::Escape("@/stores/content'"), "@/stores/content.api'" | Set-Content $_.FullName
}

# 切换回 Mock 模式
Get-ChildItem -Path src -Recurse -Filter "*.vue" | ForEach-Object {
  (Get-Content $_.FullName) -replace [regex]::Escape("@/stores/content.api'"), "@/stores/content'" | Set-Content $_.FullName
}
```

## 🔐 认证说明

### Mock 模式
- 无需登录
- 所有数据公开访问

### API 模式
- 需要认证 Token
- 未登录只能访问已发布内容
- 登录后可管理内容

### 认证流程
1. 访问 `/admin/login` 登录
2. Token 自动保存在 localStorage
3. API 请求自动携带 Token
4. Token 过期自动刷新

## 🐛 常见问题

### Q: 访问首页报 401 错误？
**A:** 说明正在使用 API 模式，但后端未运行或未登录。切换回 Mock 模式即可。

### Q: 如何判断当前使用哪个模式？
**A:** 检查页面导入语句：
```typescript
// Mock 模式
import { useContentStore } from '@/stores/content'

// API 模式
import { useContentStore } from '@/stores/content.api'
```

### Q: API 模式下 Token 刷新失败（500 错误）？
**A:** 这是后端问题，需要检查：
1. 后端是否正常运行
2. Refresh token 接口是否实现
3. 数据库连接是否正常

### Q: 部分数据在 API 模式下不显示？
**A:** 检查：
1. 后端是否已创建相应数据
2. 数据的 `draft` 状态是否为 `false`
3. 用户是否有权限访问

## 📝 开发建议

### 前期开发
推荐使用 **Mock 模式**：
- 快速开发 UI
- 无需等待后端
- 数据稳定可控

### 联调阶段
切换到 **API 模式**：
- 测试真实数据
- 验证 API 接口
- 调试认证流程

### 生产环境
必须使用 **API 模式**：
- 连接生产数据库
- 实时内容管理
- 完整功能支持

## 🎯 当前状态

✅ **项目已配置为使用 Mock 数据**

所有页面和组件都已切换回 Mock 模式，您现在可以：
1. 正常访问 `http://localhost:5173/`
2. 查看所有功能演示
3. 继续前端开发
4. 无需后端支持

## 📚 相关文档

- API 规范：`docs/api/README.md`
- API 详情：`docs/api/API-Specification.md`
- 项目状态：`docs/PROJECT-STATUS.md`

---

**更新时间：** 2025-02-04
**当前模式：** Mock 数据模式 ✅
