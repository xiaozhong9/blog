# 通知系统使用指南

## 概述

已为 Nano Banana 项目创建了完整的 Toast 通知系统，替代了控制台输出，提供更美观的用户体验。

## 架构

```
通知系统架构：
├── stores/notification.ts     # 通知状态管理
├── components/ui/ToastNotifications.vue  # Toast 通知组件
├── utils/notification.ts      # 通知工具函数
└── components/dev/DebugPanel.vue  # 开发调试面板（仅开发模式）
```

## 使用方式

### 1. 使用工具函数（推荐）

```typescript
import { notifySuccess, notifyError, notifyWarning, notifyInfo } from '@/utils/notification'

// 成功通知
notifySuccess('操作成功！', '成功')

// 错误通知
notifyError('加载失败，请重试', '错误')

// 警告通知
notifyWarning('注意：此操作不可撤销', '警告')

// 信息通知
notifyInfo('正在保存...', '提示')
```

### 2. 使用 Store

```typescript
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()

// 添加通知
notificationStore.addNotification({
  type: 'success',
  message: '操作成功',
  title: '成功',
  duration: 3000,  // 可选，默认 3000ms
})

// 便捷方法
notificationStore.success('成功消息', '标题')
notificationStore.error('错误消息', '标题')
notificationStore.warning('警告消息', '标题')
notificationStore.info('信息消息', '标题')

// 移除通知
notificationStore.removeNotification(id)

// 清空所有通知
notificationStore.clearAll()
```

### 3. 从错误对象提取消息

```typescript
import { notifyFromError } from '@/utils/notification'

try {
  await someAsyncOperation()
} catch (error) {
  notifyFromError(error, '操作失败')
}
```

## 通知类型

| 类型 | 图标 | 颜色 | 默认时长 | 用途 |
|------|------|------|----------|------|
| `success` | ✓ | 绿色 | 3000ms | 成功操作 |
| `error` | ✗ | 红色 | 5000ms | 错误提示 |
| `warning` | ⚠ | 黄色 | 3000ms | 警告信息 |
| `info` | ⓘ | 蓝色 | 3000ms | 一般信息 |

## 样式特性

- ✅ 渐变图标背景
- ✅ 左侧彩色边框
- ✅ 进度条显示剩余时间
- ✅ 平滑进入/离开动画
- ✅ 深色模式支持
- ✅ 自动堆叠显示
- ✅ 手动关闭按钮

## 已集成的位置

以下位置已替换 console 输出为通知：

### Stores
- ✅ `content.api.ts` - 内容加载错误
- ✅ `auth.api.ts` - 登录/注册成功失败

### Components
- ✅ `CommentList.vue` - 评论加载/回复/点赞错误

## 开发调试面板

开发模式下，右下角会显示调试面板，包含：

### 状态标签
- 查看文章、认证、主题、通知状态
- 实时监控应用状态

### 操作标签
- 重新加载内容
- 刷新用户信息
- 切换主题
- 清空通知

### 日志标签
- 拦截所有 console 输出
- 彩色分类显示
- 时间戳记录
- 清空日志功能

**提示**: 点击"测试通知"按钮可以快速查看所有类型的通知效果。

## 最佳实践

1. **成功操作** - 使用 `notifySuccess`
   ```typescript
   await createPost()
   notifySuccess('文章发布成功！')
   ```

2. **错误处理** - 使用 `notifyError`
   ```typescript
   try {
     await apiCall()
   } catch (e) {
     notifyError('操作失败，请稍后重试', '错误')
   }
   ```

3. **警告提示** - 使用 `notifyWarning`
   ```typescript
   if (hasUnsavedChanges) {
     notifyWarning('您有未保存的更改', '提示')
   }
   ```

4. **一般信息** - 使用 `notifyInfo`
   ```typescript
   notifyInfo('正在保存...', '请稍候')
   ```

## 自定义

### 修改样式

编辑 `ToastNotifications.vue` 中的 `typeConfig` 对象：

```typescript
const typeConfig = {
  success: {
    icon: 'lucide:check-circle',
    gradient: 'from-green-400 to-emerald-500',
    border: 'border-green-500',
  },
  // ...
}
```

### 修改位置

编辑 `ToastNotifications.vue` 中的容器样式：

```vue
<div class="fixed top-20 right-4 z-50">
  <!-- 改为其他位置，如 top-4 left-4 -->
</div>
```

### 修改时长

在 `notification.ts` 的 `addNotification` 函数中修改默认值：

```typescript
duration: notification.duration ?? (
  notification.type === 'error' ? 5000 : 3000
)
```

## 未来改进

- [ ] 添加通知音效
- [ ] 支持富文本内容
- [ ] 添加操作按钮（撤销/重试）
- [ ] 支持通知分组
- [ ] 添加通知历史记录页面
