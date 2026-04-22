# GSD 快速启动指南

欢迎使用 GSD 管理 Word 报告生成系统！本指南帮助你在 5 分钟内上手。

---

## 📁 GSD 文件位置

```
docCenter/
├── PROJECT.md              # 项目愿景（1 页纸）
├── ROADMAP.md              # 路线图和 Phase 计划
├── .planning/
│   ├── CURRENT-STATUS.md   # 📍 当前状态（每天查看）
│   ├── GSD-GUIDE.md        # 详细使用指南
│   ├── intel/              # 技术文档
│   └── phases/             # Phase 详细计划
└── PLAN.md                 # 当前激活的 Phase（运行时）
```

---

## 🚀 5 分钟上手

### Step 1: 了解项目现状（1 分钟）

```bash
# 查看当前项目状态
cat .planning/CURRENT-STATUS.md
```

**关键信息**:
- ✅ v1.0 已完成
- 🟡 v1.1 规划中（下一步）
- 🔴 需要决策：Phase 11 启动时间

### Step 2: 查看下一步计划（1 分钟）

```bash
# 查看路线图
cat ROADMAP.md | head -60
```

**下一步**: Phase 11 - 数据库模式规范化（4 天工作量）

### Step 3: 启动 Phase 11（3 分钟）

```bash
# 1. 复制 Phase 计划到活跃位置
cp .planning/phases/phase-11-database-normalization.md PLAN.md

# 2. 查看 Phase 详细任务
cat PLAN.md

# 3. 创建 TODO 列表（在编辑器中）
# 打开 PLAN.md，将任务分解为具体 TODO
```

### Step 4: 开始工作（持续）

```bash
# 每天开始工作前
cat .planning/CURRENT-STATUS.md  # 了解整体进度
cat PLAN.md                      # 查看当前任务

# 完成工作后
git add .
git commit -m "feat: Phase 11 - 完成任务 11.1"
```

---

## 📋 日常工作流程

### 每天早晨

1. **查看状态** (30 秒)
```bash
cat .planning/CURRENT-STATUS.md
```

2. **选择今日任务** (1 分钟)
```bash
cat PLAN.md | grep "\- \[ \]"  # 查看未完成的任务
```

3. **更新 TODO** (2 分钟)
```bash
# 使用 todowrite 工具创建今日 TODO 列表
```

### 每天结束

1. **提交代码**
```bash
git add .
git commit -m "feat: Phase 11 - [完成的任务]"
```

2. **更新状态** (1 分钟)
```bash
# 编辑 .planning/CURRENT-STATUS.md
# 更新"本周进展"部分
```

---

## 🎯 关键决策点

### 决策 1: 何时启动 Phase 11？

**建议**: 立即启动（P0 优先级）

**理由**:
- 数据库问题是当前最大技术债务
- 影响后续所有 Phase
- 工作量可控（4 天）

**行动**: 
```bash
cp .planning/phases/phase-11-database-normalization.md PLAN.md
```

### 决策 2: 数据库迁移策略？

**选项 A**: 一次性迁移
- ✅ 优点：干净彻底，无历史包袱
- ❌ 缺点：风险高，需要停机

**选项 B**: 渐进式迁移
- ✅ 优点：风险低，可回滚
- ❌ 缺点：需要兼容层，工作量大

**建议**: 选项 B（渐进式），通过 property 保持向后兼容

### 决策 3: 测试框架选择？

**后端**: pytest（Python 标准）
**前端**: Vitest（Vite 生态）或保持 Playwright（E2E）

**建议**: 
- 后端：pytest + pytest-asyncio
- 前端：Vitest（单元测试）+ Playwright（E2E）

---

## 📞 需要帮助？

### 查看文档

```bash
# 详细使用指南
cat .planning/GSD-GUIDE.md

# 项目愿景
cat PROJECT.md

# 技术栈文档
cat .planning/intel/tech-stack.md
```

### 常见问题

**Q: 如何添加新 Phase？**
```bash
# 1. 在 ROADMAP.md 中添加 Phase 描述
# 2. 创建 .planning/phases/phase-XX-description.md
# 3. 更新 .planning/CURRENT-STATUS.md
```

**Q: 如何标记 Phase 完成？**
```bash
# 1. 确认所有 TODO 已完成
# 2. 更新 ROADMAP.md 标记 Phase 为 ✅
# 3. 创建 git tag
git tag -a v1.1-phase-11-complete -m "Phase 11 完成"
```

**Q: 如何处理延期？**
```bash
# 1. 更新 PLAN.md 中的时间估算
# 2. 更新 .planning/CURRENT-STATUS.md 说明原因
# 3. 通知相关人员
```

---

## 🔗 下一步行动

### 立即执行（今天）

1. **启动 Phase 11**
```bash
cp .planning/phases/phase-11-database-normalization.md PLAN.md
```

2. **创建 TODO 列表**
- 任务 11.1: 设计 ERD（0.5 天）
- 任务 11.2: 创建关联表模型（0.5 天）

3. **开始工作**
```bash
# 打开编辑器开始设计 ERD
```

### 本周完成

- ✅ 启动 Phase 11
- ✅ 完成任务 11.1-11.3（模型设计）
- ✅ 提交第一次代码

### 下周完成

- ✅ 完成任务 11.4-11.6（迁移和验证）
- ✅ Phase 11 验收
- ✅ 启动 Phase 12

---

## 📊 成功指标

**Phase 11 完成标准**:
- [ ] 新模型通过 SQLAlchemy 创建
- [ ] 数据库迁移脚本执行成功
- [ ] 现有数据成功迁移
- [ ] 所有 API 测试通过
- [ ] 回滚方案已验证

**项目健康度提升**:
- 技术债务：🟡 中等 → 🟢 低
- 代码质量：🟡 中等 → 🟢 良好
- 测试覆盖：🔴 不足 → 🟡 中等（Phase 14 后）

---

**祝你工作顺利！** 🚀

有任何问题，查看 `.planning/GSD-GUIDE.md` 获取详细指南。
