# GSD 使用指南

本文件说明如何在 Word 报告生成系统中使用 GSD (Goal-Structured Development) 工作流。

---

## 1. GSD 核心文件结构

```
docCenter/
├── PROJECT.md                          # 项目愿景、目标、核心价值
├── ROADMAP.md                          # 里程碑和 Phase 计划
├── .planning/
│   ├── intel/                          # 技术情报和知识库
│   │   ├── tech-stack.md              # 技术栈详细文档
│   │   └── codebase-structure.md      # 代码库结构文档
│   └── phases/                         # Phase 详细计划
│       └── phase-11-database-normalization.md
└── PLAN.md                             # 当前激活的 Phase 计划（运行时生成）
```

---

## 2. 核心概念

### 2.1 Milestone (里程碑)

**定义**: 项目的重大版本节点，代表一组相关功能的完成。

**当前里程碑**:
- ✅ v1.0 - 初始化版本（已完成）
- 🟡 v1.1 - 架构改进（规划中）
- ⚪ v1.2 - 功能增强（待规划）
- ⚪ v2.0 - 生产就绪（待规划）

### 2.2 Phase (阶段)

**定义**: Milestone 中的具体工作单元，有明确的验收标准和交付物。

**Phase 编号规则**: `里程碑版本号。Phase 序号`
- 例：`Phase 11` = v1.1 的第 1 个 Phase
- 例：`Phase 12.1` = v1.1 的第 2 个 Phase 的子任务

### 2.3 TODO (待办事项)

**定义**: Phase 中的具体任务，可分配给个人执行。

**状态**:
- 📋 Pending - 待开始
- 🔄 In Progress - 进行中
- ✅ Completed - 已完成
- ❌ Blocked - 被阻塞

---

## 3. 工作流程

### 3.1 开始新 Phase

```bash
# 1. 查看 ROADMAP.md 选择下一个 Phase
# 2. 创建 Phase 计划文件
touch .planning/phases/phase-XX-description.md

# 3. 激活 Phase（创建 PLAN.md）
cp .planning/phases/phase-XX-description.md PLAN.md

# 4. 开始执行 Phase 中的 TODO 项
```

### 3.2 执行 Phase

```bash
# 1. 查看当前 Phase 计划
cat PLAN.md

# 2. 创建 TODO 列表（使用 todowrite 工具）
# 3. 逐项完成 TODO
# 4. 更新进度标记

# 5. 完成 Phase 后
git add .
git commit -m "feat: complete Phase XX - [description]"
```

### 3.3 完成 Milestone

```bash
# 1. 确认所有 Phase 已完成
# 2. 运行验收测试
# 3. 更新 ROADMAP.md 标记 Milestone 状态
# 4. 创建 Git 标签
git tag -a v1.1 -m "Release v1.1 - 架构改进"
git push origin v1.1
```

---

## 4. 文件更新规范

### 4.1 PROJECT.md

**更新时机**:
- 项目愿景变更
- 技术栈重大调整
- 目标用户群体变化

**维护频率**: 每季度审查一次

### 4.2 ROADMAP.md

**更新时机**:
- 新 Milestone 规划完成
- Phase 计划变更
- Milestone 状态更新

**维护频率**: 每 Phase 结束后更新

### 4.3 Phase 文件

**更新时机**:
- Phase 开始时创建
- 任务完成后更新进度
- Phase 结束时标记完成

**维护频率**: 实时跟踪

---

## 5. 进度追踪

### 5.1 每日站会

```markdown
## YYYY-MM-DD 站会

### 昨日完成
- [ ] Phase XX - Task YY: 完成内容

### 今日计划
- [ ] Phase XX - Task ZZ: 计划内容

### 阻塞问题
- [ ] 问题描述，需要谁协助
```

### 5.2 每周审查

```bash
# 查看本周 git 提交
git log --since="1 week ago" --oneline

# 查看 Phase 进度
cat ROADMAP.md | grep -A 20 "Phase XX"

# 更新 TODO 状态
```

---

## 6. 最佳实践

### 6.1 Phase 规划

✅ **推荐**:
- Phase 工作量 1-5 天
- 有明确的验收标准
- 依赖关系清晰
- 风险已识别

❌ **避免**:
- Phase 超过 1 周
- 验收标准模糊
- 依赖未识别
- 无回滚方案

### 6.2 TODO 管理

✅ **推荐**:
- TODO 细化到 0.5-1 天工作量
- 及时更新状态
- 阻塞问题立即标记
- 完成一个勾一个

❌ **避免**:
- TODO 粒度过大（>3 天）
- 状态不更新
- 阻塞问题不报告
- 批量勾选 TODO

### 6.3 文档维护

✅ **推荐**:
- 代码和文档同步更新
- 变更及时记录
- 使用中文文档
- 保持格式一致

❌ **避免**:
- 代码变了文档不变
- 事后补文档
- 中英文混用
- 格式混乱

---

## 7. 工具和命令

### 7.1 GSD 相关命令

```bash
# 查看项目状态
cat PROJECT.md | grep "当前状态"

# 查看路线图
cat ROADMAP.md

# 查看当前 Phase
cat PLAN.md

# 查看 Phase 列表
ls -la .planning/phases/
```

### 7.2 Git 命令

```bash
# 查看当前分支
git branch

# 查看未提交变更
git status

# 创建功能分支
git checkout -b feature/phase-11

# 提交代码
git add .
git commit -m "feat: Phase 11 - [具体任务]"

# 推送分支
git push origin feature/phase-11
```

---

## 8. 角色与职责

| 角色 | 职责 | 权限 |
|------|------|------|
| 项目负责人 | 审批 Milestone 计划、资源协调 | 批准 Phase 优先级 |
| 技术负责人 | 技术决策、代码审查 | 批准技术方案 |
| 开发者 | 执行 Phase、完成 TODO | 创建 Phase 计划 |
| 测试人员 | 验收测试、质量把关 | 否决未达标 Phase |

---

## 9. 常见问题

### Q1: Phase 做了一半发现需要调整怎么办？

**A**: 
1. 更新 Phase 计划文档
2. 评估对时间和依赖的影响
3. 通知相关人员
4. 继续执行

### Q2: 多个 Phase 可以并行吗？

**A**: 
- 无依赖关系的 Phase 可以并行
- 有依赖关系的 Phase 必须串行
- 在 ROADMAP.md 中标注依赖关系

### Q3: 如何评估 Phase 工作量？

**A**:
- 任务分解到 0.5-1 天粒度
- 参考历史类似任务
- 增加 20% 缓冲时间
- 团队讨论评估

### Q4: Phase 延期了怎么办？

**A**:
1. 分析延期原因
2. 评估是否需要调整范围
3. 更新 ROADMAP.md 时间线
4. 通知相关人员
5. 记录经验教训

---

## 10. 变更历史

| 日期 | 版本 | 变更内容 | 作者 |
|------|------|----------|------|
| 2024-04-22 | v1.0 | 初始版本 | GSD |

---

## 附录：模板文件

### Phase 计划模板

```markdown
# Phase XX: [名称]

**Milestone**: v1.X  
**优先级**: P0/P1/P2  
**状态**: 📋 待开始  
**预计工作量**: X 天  
**负责人**: TBD

## 1. 目标与背景
[问题陈述和解决方案]

## 2. 任务分解
[任务列表和验收标准]

## 3. 风险与缓解
[风险识别和应对措施]

## 4. 验收标准
[技术验收、代码质量、文档]

## 5. 依赖关系
[前置依赖和后续依赖]

## 6. 估算与时间线
[任务分解时间表]

## 7. 备注
[其他需要注意的事项]
```

### TODO 模板

```markdown
- [ ] XX.X: [任务名称]
  - **工作量**: X 小时/天
  - **输出**: [交付物]
  - **验收**: [验收标准]
```
