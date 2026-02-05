---
title: "使用 Tailwind CSS 构建设计系统"
description: "学习如何使用 Tailwind CSS 设计令牌构建可扩展的设计系统。"
date: "2024-02-01"
tags: ["tailwind", "design", "css"]
category: "blog"
locale: "zh"
featured: true
draft: false
---

# 使用 Tailwind CSS 构建设计系统

Tailwind CSS 是一个功能类优先的 CSS 框架，非常适合构建设计系统。

## 设计令牌

首先定义你的设计令牌：

```javascript
// tailwind.config.js
export default {
  theme: {
    extend: {
      colors: {
        primary: {
          from: '#60A5FA',
          to: '#A78BFA',
        },
      },
    },
  },
}
```

## 组件模式

### 1. 基础组件

```vue
<template>
  <button class="px-4 py-2 rounded-xl bg-gradient-to-r from-primary-from to-primary-to">
    Click me
  </button>
</template>
```

### 2. 组合组件

```vue
<template>
  <div class="card">
    <h2 class="card-title">Title</h2>
    <p class="card-text">Content</p>
  </div>
</template>
```

## 最佳实践

1. **使用 `@apply` 提取重复样式**
2. **配置 `theme.extend` 而不是覆盖**
3. **使用 `@layer` 组织样式**
4. **保持一致的间距和比例**

## 总结

Tailwind CSS 让你能够:
- 🎨 快速构建 UI
- 📏 保持设计一致性
- 🔄 轻松定制主题
- 📦 生成优化的 CSS
