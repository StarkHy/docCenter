---
phase: 16-dynamic-chart-data
plan: '01'
subsystem: chart
tags: [chart, datasource, dynamic-binding]
dependency_graph:
  requires: []
  provides: [B06]
  affects: [document_generation_service, mapping]
tech_stack:
  added: []
  patterns: [dynamic-data-binding, datasource-field-mapping]
key_files:
  modified:
    - word-report-backend/app/services/document_generation_service.py
    - word-report-generator/src/views/Mapping.vue
decisions:
  - decision: 动态/静态双模式兼容
    rationale: 保留现有静态数据配置兼容性，新增字段映射配置时优先使用动态数据
---

# Phase 16: 图表数据动态绑定 — Summary

## 执行结果: ✅ 已完成

**目标**: 实现图表配置与数据源分离，图表数据从数据源动态获取。

---

## 完成的 Tasks

| Task | Name | Status | Commit |
|------|------|--------|--------|
| 16.1 | 后端数据源字段映射 (enrich) | ✅ | 843f8f1 |
| 16.2 | 兼容已有图表配置 | ✅ | 843f8f1 |
| 16.3 | 前端图表配置 UI | ✅ | 843f8f1 |
| - | Bugfix: 恢复动态数据绑定 | ✅ | 7bd4936 |

---

## 实现详情

### 16.1: 后端数据源字段映射

**文件**: `word-report-backend/app/services/document_generation_service.py`

新增 `_enrich_chart_from_datasource()` 方法：

```python
def _enrich_chart_from_datasource(self, chart_config: dict, datasource_data: dict) -> dict:
    ds_id = chart_config.get("datasource_id")
    if not ds_id or ds_id not in datasource_data:
        return chart_config        # 无数据源 → 使用静态数据
    
    data = datasource_data[ds_id]
    x_field = chart_config.get("x_field")
    y_field = chart_config.get("y_field")
    
    if isinstance(data, list):
        x_data = [str(row.get(x_field, "")) for row in data]
        y_data = [float(row.get(y_field, 0)) for row in data]
        chart_config["x_data"] = x_data
        chart_config["y_data"] = y_data
```

修改 `_generate_charts_for_document()`：
- 自动为含 `datasource_id` 的图表配置调用 enrich
- enrich 后调用 `chart_service.generate_charts()` 生成图片

### 16.2: 兼容性

- 不含 `datasource_id` 的旧配置：直接使用 `x_data`/`y_data` 静态数据 ✅
- 特殊图表类型 (settlement_duration, waterlevel_duration, comparison)：
  保留原有数据处理逻辑，支持 JSON 复杂数据结构 ✅
- 多数据源：每个图表配置独立指定 datasource_id ✅

### 16.3: 前端 UI

**文件**: `word-report-generator/src/views/Mapping.vue`

图表配置区新增：
- **数据源下拉选择器**: 从已选数据源列表中选（`chart.datasource_id`）
- **X轴字段下拉选择器**: 选中数据源后动态加载字段列表（`chart.x_field`）
- **Y轴字段下拉选择器**: 同上（`chart.y_field`）
- **动态/静态模式切换**: 选择数据源后隐藏静态数据输入区
- **单位字段**: 图表 Y 轴单位配置（`chart.unit`）
- **提交处理**: 动态模式发送 field 配置，静态模式发送 csv → array 数据
- **编辑回填**: 完整支持动态配置的编辑回填

## 数据流

```
用户 → Mapping.vue 配置图表
       ├─ 选数据源 + x/y 字段 (动态模式)
       └─ 直接输入 x_data, y_data (静态模式)
       ↓
保存到 MappingChart.chart_config
       ↓
生成文档时:
  _fetch_multiple_datasources → 获取所有数据源数据
  _apply_field_mapping_multi → 字段映射
  _generate_charts_for_document:
    _enrich_chart_from_datasource → 提取动态数据
    chart_service.generate_charts → 生成图表图片
  → 插入 Word 文档
```

## 验收标准

- [x] 图表配置时可选择数据源字段作为 x/y 轴 ✅
- [x] 图表数据从配置的 datasource 动态获取 ✅
- [x] 图表标题、单位等样式可在映射中配置 ✅
- [x] 支持静态数据和动态数据两种模式（兼容现有）✅
- [x] 生成文档时正确渲染动态数据的图表 ✅

## Commits

| Hash | Message |
|------|---------|
| `843f8f1` | feat: implement B06 chart dynamic data binding |
| `7bd4936` | fix: restore chart dynamic data binding |

## Verification

- [x] 后端 enrich 逻辑存在且正确
- [x] 前端图表配置 UI 完整
- [x] 动态/静态双模式兼容
- [x] 特殊图表类型不受影响
- [x] 已有映射配置可正常编辑
