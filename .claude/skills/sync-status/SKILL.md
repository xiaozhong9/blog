---
name: sync-status
description: 更新 Nano Banana 博客项目的 SYSTEM_STATUS.md 文档，记录项目当前状态
allowed_tools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
---

# Nano Banana 博客 - 系统状态同步工作流

你负责保持项目 SYSTEM_STATUS.md 文档与代码库同步，确保 AI 和用户随时了解项目真实状态。

## 工作流程

### 第一步：分析代码变更

1. **使用 git status 查看变更**
   ```bash
   cd p:/workspace/blog
   git status
   git diff --stat
   ```

2. **识别变更类型**
   - 新增功能
   - Bug 修复
   - 架构调整
   - 配置变更
   - 文档更新

### 第二步：探索代码库状态

3. **统计文件数量**（如需要）
   ```bash
   # 前端页面
   ls p:/workspace/blog/frontend/src/pages/*/*.vue 2>/dev/null | wc -l

   # 前端组件
   find p:/workspace/blog/frontend/src/components -name "*.vue" 2>/dev/null | wc -l

   # 后端模型
   find p:/workspace/blog/backend -name "models.py" 2>/dev/null | wc -l
   ```

4. **检查功能实现状态**
   - 使用 Grep 搜索特定功能标记
   - 查看测试文件（如存在）
   - 检查配置文件

### 第三步：更新文档

5. **读取当前 SYSTEM_STATUS.md**
   - 使用 Read 工具读取 `p:\workspace\blog\SYSTEM_STATUS.md`
   - 对比代码实际状态
   - 识别需要更新的部分

6. **更新对应章节**

   **整体进度表**
   - 更新完成度百分比
   - 更新状态符号（✅/⚠️/❌）
   - 更新最后修改日期

   **前端状态**
   - [ ] 添加新页面到列表
   - [ ] 添加新组件到列表
   - [ ] 更新功能实现状态
   - [ ] 更新技术债务

   **后端状态**
   - [ ] 更新模型完成度
   - [ ] 更新 API 实现状态
   - [ ] 更新已知问题
   - [ ] 更新待办事项

   **集成状态**
   - [ ] 更新 API 对接情况
   - [ ] 更新数据适配器状态

   **测试状态**
   - [ ] 更新测试覆盖率
   - [ ] 记录新增测试

### 第四步：验证与记录

7. **更新元数据**
   ```yaml
   ---
   version: "0.x.x"  # 如果有重大更新
   last_updated: "YYYY-MM-DD"
   updated_by: "AI Assistant"
   ---
   ```

8. **添加版本记录**
   ```markdown
   | 版本 | 日期 | 变更摘要 | 作者 |
   |------|------|----------|------|
   | 0.x.x | YYYY-MM-DD | [变更描述] | AI Assistant |
   ```

9. **更新检查清单**
   - [ ] 整体进度百分比正确
   - [ ] 前端状态准确
   - [ ] 后端状态准确
   - [ ] 集成状态准确
   - [ ] 测试状态准确
   - [ ] 技术债务已更新
   - [ ] 待办事项已更新
   - [ ] last_updated 已更新
   - [ ] 版本历史已添加

## 状态标记规范

### 功能级别
- ✅ 已完成 (100%)
- ⚠️ 部分完成 (50-99%)
- ❌ 未实现 (0-49%)

### 任务级别
- [x] 已完成
- [ ] 未完成
- [~] 进行中

### 问题级别
- 🐛 Bug
- ⚠️ 警告
- 💡 优化建议
- 📝 文档待补充

## 更新触发条件

**必须更新**：
- ✅ 完成功能模块后
- ✅ 修复关键 Bug 后
- ✅ 架构调整后
- ✅ 用户明确要求时

**建议更新**：
- 💡 每日工作结束时
- 💡 完成重要里程碑后

## 项目特定信息

**项目名称**：Nano Banana Blog
**前端路径**：`p:\workspace\blog\frontend`
**后端路径**：`p:\workspace\blog\backend`
**状态文档**：`p:\workspace\blog\SYSTEM_STATUS.md`

## 输出示例

```markdown
## 📝 状态同步完成

**更新时间**：YYYY-MM-DD

**更新内容**：
- ✅ 前端：新增 [功能名] 页面
- ✅ 后端：实现 [API名] 端点
- ⚠️ 集成：[API名] 对接中
- 🐛 修复：[Bug描述]

**进度变化**：
- 搜索功能：40% → 60%
- 整体完成度：75% → 78%

**文档已更新**：
- p:\workspace\blog\SYSTEM_STATUS.md
- 版本记录已添加
```

## 注意事项

- ⚠️ 更新前先读取当前文档，避免覆盖
- ⚠️ 保持客观真实，不夸大进度
- ⚠️ 使用统一的格式和符号
- ⚠️ 定期清理过期的待办事项（建议每月）
