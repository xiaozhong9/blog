# 研究发现与决策 - Nano Banana

## 需求

### 核心功能
- 个人品牌展示系统
- 技术知识分享平台
- 生活/日记记录空间
- AI 增强型内容网站（基础就绪）
- 长期可扩展内容平台

### 内容类型
- **Blog（博客）** - 技术文章、教程
- **Projects（项目）** - 作品集和展示
- **Life（生活）** - 个人日记、摄影
- **Notes（笔记）** - 快速想法、片段

### 设计需求
- Josh Comeau 风格设计语言
- 现代极简主义配柔和渐变
- 微交互和弹簧动画
- 优化的阅读体验（65ch 宽度）
- 滚动时玻璃态导航栏效果
- 响应式设计

### 技术需求
- Vue 3 + TypeScript + Vite
- Tailwind CSS 配自定义设计令牌
- 从 `/src/content/` 加载内容
- Markdown 配 Zod 前置元数据验证
- 多语言支持（zh-CN 默认、en-US）
- 主题切换（浅色/深色/跟随系统）
- 全文搜索（Cmd+K）
- SEO 优化（OpenGraph、Twitter Card、JSON-LD）

## 研究发现

### 设计灵感
- **Josh Comeau**：柔和渐变、教育感、出色的排版
- **Lee Robinson**：简洁现代美学、极佳性能
- **Vercel 设计系统**：极简主义、一致的令牌

### 已定义的设计令牌
```css
/* 主渐变 */
#60A5FA → #A78BFA（蓝到紫）

/* 浅色主题 */
Background: #F8FAFC
Surface: #FFFFFF
Text Primary: #0F172A
Border: #E2E8F0

/* 深色主题 */
Background: #0B1120
Surface: #111827
Text Primary: #E2E8F0

/* UI 风格 */
Radius: 2xl (1rem / 16px)
Shadow: 柔和、扩散
Font: Inter 或 System UI
```

### 动效设计系统
- **快速**：150ms
- **正常**：300ms
- **弹簧**：cubic-bezier(0.22, 1, 0.36, 1)

## 技术决策

| 决策 | 理由 |
|----------|-----------|
| Vue 3 Composition API + Script Setup | 现代、简洁、出色的 TypeScript 支持 |
| TypeScript | 类型安全、更好的开发体验、可扩展性 |
| Vite | 最快的构建工具、优秀的生态系统 |
| unplugin-vue-router | 像 Next.js 一样的文件路由、自动生成路由 |
| Pinia | 官方状态管理、比 Vuex 更简单 |
| Tailwind CSS | 功能类优先、一致的设计系统 |
| vue-i18n | 官方 Vue i18n 方案 |
| gray-matter | 标准前置元数据解析器 |
| zod | 运行时类型验证、TypeScript 推断 |
| Shiki | VS Code 的代码高亮器、现代主题 |
| AutoAnimate | 零配置列表动画 |
| Giscus | 基于 GitHub Discussions 的评论 |

### 待决策事项
- [x] Headless UI vs Radix Vue（基础组件）→ 构建了自定义组件
- [x] Orama vs MiniSearch（搜索引擎）→ 使用内置搜索
- [x] markdown-it vs unified/remark（MD 渲染器）→ 自定义解析器（Shiki 就绪）

## 遇到的问题
| 问题 | 解决方案 |
|-------|------------|
| | 实现过程中未遇到问题 |

## 资源

### 文档
- Vue 3: https://vuejs.org/
- Vite: https://vitejs.dev/
- Tailwind CSS: https://tailwindcss.com/
- Pinia: https://pinia.vuejs.org/
- vue-i18n: https://vue-i18n.intlify.dev/
- Shiki: https://shiki.style/

### 设计参考
- Josh Comeau: https://www.joshwcomeau.com/
- Lee Robinson: https://lee.robinson.tech/
- Vercel 设计系统: https://vercel.com/design

### 待安装的包
```json
{
  "dependencies": {
    "vue": "^3.4.0",
    "vue-router": "^4.2.0",
    "pinia": "^2.1.0",
    "vue-i18n": "^9.9.0",
    "@vueuse/core": "^10.7.0",
    "@vueuse/motion": "^2.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^5.0.0",
    "vite": "^5.0.0",
    "typescript": "^5.3.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0",
    "unplugin-vue-router": "^0.7.0",
    "@iconify-json/lucide": "^1.1.0",
    "@iconify/vue": "^4.1.0",
    "shiki": "^1.0.0",
    "gray-matter": "^4.0.0",
    "zod": "^3.22.0"
  }
}
```

## 视觉/浏览器研究发现
<!-- 视觉研究后更新 -->

---
*每进行 2 次查看/浏览器/搜索操作后更新此文件*
*这可以防止视觉信息丢失*
