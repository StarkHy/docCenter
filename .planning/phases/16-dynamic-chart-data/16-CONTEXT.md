---
phase: 16-dynamic-chart-data
type: context
created: 2026-04-27
status: locked
---

# Phase 16: 图表数据动态绑定 — Context

## 目标

实现图表配置与数据源分离，让图表数据从数据源动态获取，而非在映射配置中硬编码静态数据。

## 当前状态（已实现的部分）

基于最近的提交记录和代码审查，部分功能已经实现：

### ✅ 已完成

1. **后端动态数据绑定** (`document_generation_service.py:458-482`)
   - `_enrich_chart_from_datasource()`：根据 chart_config 中的 `datasource_id`、`x_field`、`y_field` 从数据源获取数据并注入图表
   - `_generate_charts_for_document()`：在生成图表前自动调用了 enrich 方法

2. **数据库模型支持** (`models.py` / `MappingChart`)
   - `chart_config` 字段可存储动态绑定配置（包括 x_field, y_field, datasource_id 等）
   - Mapping API 返回的 chart_config 已包含完整配置信息

3. **特殊图表类型**
   - 已支持：沉降历时曲线、地下水位历时曲线、分层标对比图
   - 这些图表类型的数据结构较复杂（多系列、分层数据）

### ❌ 待实现

1. **前端 UI** — Mapping.vue 中的图表配置表单
   - 需要支持从已选数据源选择字段作为 x_field / y_field
   - 需要区分"静态数据"和"动态绑定"两种模式
   - 多系列图表（多条折线/柱状）的配置 UI

2. **端到端测试验证**
   - 动态数据绑定 → 图表生成 → 文档嵌入 的完整流程测试

## 关键决策

| 决策 | 选择 | 理由 |
|------|------|------|
| 动态/静态模式 | 兼容两种模式 | 保留现有静态数据兼容性，新增字段映射时优先使用动态数据 |
| 多系列支持 | 后端已支持，前端待完善 | 多个 datasource 或同一数据源的多列映射 |
| 图表类型扩展 | 保持现有 7 种类型 | 不需要新增图表类型，只需让已有类型支持动态数据 |

## 任务分解确认

沿用阶段定义文件中的任务分解：

1. **16.1 数据源字段映射到图表** — ✅ 后端已完成
2. **16.2 图表配置增强** — 需确认前端实现
3. **16.3 后端数据获取逻辑** — ✅ 已完成
4. **16.4 前端 UI 更新** — ❌ 待实现

## 技术方案

### 数据流
```
用户配置映射(含图表) → 保存到 MappingChart.chart_config
生成文档时:
  1. 获取所有数据源数据 (_fetch_multiple_datasources)
  2. 字段映射到 context (_apply_field_mapping_multi)
  3. 对每个图表：
     - 如果有 datasource_id + x_field + y_field:
       → _enrich_chart_from_datasource: 从数据源提取数据
     - 如果已经是静态数据 (x_data, y_data):
       → 直接使用
  4. 调用 chart_service.generate_charts 生成图片
  5. 插入到 Word 文档
```

### 前端设计思路
- Mapping.vue 的图表配置对话框需要增加：
  - 数据源下拉选择（从已选数据源列表中选）
  - X 轴字段下拉选择（从选中数据源的字段中选）
  - Y 轴字段下拉选择
  - 单位/颜色方案等样式配置
  - "静态数据"与"动态数据"的切换开关
