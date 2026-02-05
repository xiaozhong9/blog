# AI 聊天助手配置指南

## 功能说明

已集成 **Anthropic Claude AI** 聊天助手，提供以下功能：

- ✅ 智能问答：回答关于博客内容的问题
- ✅ 文章推荐：根据用户兴趣推荐相关文章
- ✅ 内容总结：快速总结文章要点
- ✅ 技术咨询：提供前端开发建议和见解

## 配置步骤

### 1. 获取 Anthropic API Key

1. 访问 [Anthropic Console](https://console.anthropic.com/)
2. 注册或登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key
5. 复制 API Key（只显示一次，请妥善保存）

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：

```bash
# 复制示例配置文件
cp .env.example .env
```

编辑 `.env` 文件，添加你的 API Key：

```env
VITE_ANTHROPIC_API_KEY=sk-ant-your-actual-api-key-here
```

### 3. 重启开发服务器

```bash
# 停止当前服务器 (Ctrl+C)
# 重新启动
npm run dev
```

## 使用方法

1. 点击右下角的 **聊天图标** 打开 AI 助手
2. 输入问题并发送
3. AI 会基于上下文智能回答

### 示例问题

- "这篇博客讲了什么？"
- "推荐一些 Vue 3 相关的文章"
- "如何优化前端性能？"
- "总结一下这篇文章的要点"

## 模型选择

默认使用 **Claude 3 Haiku**（快速、经济）

可切换到其他模型（在 `src/utils/anthropic.ts` 中修改）：

| 模型 | 特点 | 适用场景 |
|------|------|---------|
| **Haiku** | 最快、最便宜 | 简单问答、快速响应 |
| **Sonnet** | 平衡性能和成本 | 一般对话、内容分析 |
| **Opus** | 最强大、最贵 | 复杂推理、深度分析 |

## 安全提示

⚠️ **重要：API Key 安全**

1. **切勿将 `.env` 文件提交到 Git**
   - `.env` 已在 `.gitignore` 中
   - 只提交 `.env.example` 作为模板

2. **生产环境**
   - 使用环境变量或密钥管理服务
   - 考虑使用代理服务器隐藏 API Key
   - 启用速率限制防止滥用

3. **浏览器中的 API Key**
   - 当前配置直接在浏览器中调用 API
   - 适合个人博客和开发环境
   - 生产环境建议通过后端代理

## 费用说明

Claude 3 模型定价（2024年）：

| 模型 | 输入 | 输出 |
|------|------|------|
| Haiku | $0.25/百万token | $1.25/百万token |
| Sonnet | $3/百万token | $15/百万token |
| Opus | $15/百万token | $75/百万token |

**估算：** 个人博客每月几美元即可满足需求

## 故障排除

### 1. "API key is missing" 错误
- 检查 `.env` 文件是否存在
- 确认 `VITE_ANTHROPIC_API_KEY` 已正确设置
- 重启开发服务器

### 2. "API Error" 错误
- 验证 API Key 是否有效
- 检查网络连接
- 确认 API 额度是否充足

### 3. AI 回复无关内容
- 可以在 `src/stores/aiChat.ts` 中调整 `systemPrompt`
- 添加更多博客上下文信息

## 自定义配置

### 修改系统提示词

编辑 `src/stores/aiChat.ts`：

```typescript
const systemPrompt = `你是一个专业的博客助手...
- 博客名称：你的博客名
- 主题：你的主题
- ...`
```

### 调整聊天窗口样式

编辑 `src/components/ai/AIChatAssistant.vue`：

```vue
<style>
/* 自定义样式 */
</style>
```

## 后续扩展

可以考虑添加：

- [ ] 联网搜索功能（让 AI 搜索最新信息）
- [ ] 文章内容注入（将当前文章内容注入上下文）
- [ ] 多语言支持优化
- [ ] 聊天历史持久化（保存到 localStorage）
- [ ] 语音输入支持

## 帮助

如有问题，请参考：
- [Anthropic 文档](https://docs.anthropic.com/)
- [Claude API 参考](https://docs.anthropic.com/claude/reference)
- [项目 Issues](https://github.com/your-repo/issues)
