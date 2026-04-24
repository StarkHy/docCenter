# 数据库 ERD (Entity Relationship Diagram)

**版本**: v2.0 (规范化版本)  
**创建日期**: 2024-04-22  
**Phase**: 11.1

---

## 1. 实体关系图

```
┌─────────────────────┐
│     Template        │
├─────────────────────┤
│ PK id               │
│    name             │
│    category         │
│    file_name        │
│    file_path        │
│    file_size        │
│    variables (JSON) │
│    create_time      │
└─────────────────────┘
         │
         │ 1:N
         │
         ▼
┌─────────────────────┐       ┌─────────────────────────┐
│      Mapping        │◄──────┤  MappingDataSource      │
├─────────────────────┤       ├─────────────────────────┤
│ PK id               │       │ PK,FK mapping_id        │
│    name             │       │ PK,FK datasource_id     │
│    template_id (FK) │       │    order                │
│    create_time      │       └─────────────────────────┘
└─────────────────────┘                  │
         │                               │ FK
         │ 1:N                           │
         │                               ▼
         │                      ┌─────────────────────┐
         │                      │    DataSource       │
         │                      ├─────────────────────┤
         │                      │ PK id               │
         │                      │    name             │
         │                      │    type             │
         │                      │    config (JSON)    │
         │                      │    status           │
         │                      │    create_time      │
         │                      │    update_time      │
         │                      └─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────────┐
│    MappingChart         │
├─────────────────────────┤
│ PK id                   │
│    mapping_id (FK)      │
│    chart_id             │
│    chart_type           │
│    chart_title          │
│    chart_config (JSON)  │
└─────────────────────────┘

┌─────────────────────┐
│  DocumentHistory    │
├─────────────────────┤
│ PK id               │
│    mapping_id (FK)  │
│    template_id (FK) │
│    datasource_ids   │
│    output_filename  │
│    file_path        │
│    status           │
│    error_message    │
│    create_time      │
└─────────────────────┘
```

---

## 2. 数据表详细定义

### 2.1 Template (模板表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 模板 ID |
| name | VARCHAR(255) | NOT NULL | 模板名称 |
| category | VARCHAR(100) | NULL | 分类 |
| file_name | VARCHAR(255) | NOT NULL | 文件名 |
| file_path | VARCHAR(500) | NOT NULL | 存储路径 |
| file_size | INTEGER | NOT NULL | 文件大小（字节） |
| variables | JSON | DEFAULT [] | 模板变量列表 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

---

### 2.2 DataSource (数据源表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 数据源 ID |
| name | VARCHAR(255) | NOT NULL | 数据源名称 |
| type | VARCHAR(50) | NOT NULL | 类型（http_api/json/form） |
| config | JSON | DEFAULT {} | 配置信息 |
| status | VARCHAR(50) | DEFAULT 'inactive' | 状态 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |
| update_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 更新时间 |

---

### 2.3 Mapping (映射配置表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 映射 ID |
| name | VARCHAR(255) | NOT NULL | 映射名称 |
| template_id | INTEGER | FOREIGN KEY → templates(id) | 关联模板 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 创建时间 |

**外键约束**:
```sql
FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE CASCADE
```

---

### 2.4 MappingDataSource (映射 - 数据源关联表) ⭐ 新增

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| mapping_id | INTEGER | PRIMARY KEY, FOREIGN KEY | 映射 ID |
| datasource_id | INTEGER | PRIMARY KEY, FOREIGN KEY | 数据源 ID |
| order | INTEGER | DEFAULT 0, NOT NULL | 排序顺序 |

**外键约束**:
```sql
FOREIGN KEY (mapping_id) REFERENCES mappings(id) ON DELETE CASCADE
FOREIGN KEY (datasource_id) REFERENCES datasources(id) ON DELETE CASCADE
```

**唯一约束**:
```sql
PRIMARY KEY (mapping_id, datasource_id)
```

---

### 2.5 MappingChart (映射图表配置表) ⭐ 新增

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 图表 ID |
| mapping_id | INTEGER | FOREIGN KEY, NOT NULL | 映射 ID |
| chart_id | VARCHAR(100) | NOT NULL | 图表唯一标识 |
| chart_type | VARCHAR(50) | NULL | 图表类型 |
| chart_title | VARCHAR(255) | NULL | 图表标题 |
| chart_config | JSON | DEFAULT {} | 图表完整配置 |

**外键约束**:
```sql
FOREIGN KEY (mapping_id) REFERENCES mappings(id) ON DELETE CASCADE
```

**唯一约束**:
```sql
UNIQUE (mapping_id, chart_id)
```

**索引**:
```sql
CREATE INDEX idx_chart_id ON mapping_charts(chart_id);
```

---

### 2.6 DocumentHistory (文档历史表)

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 历史记录 ID |
| mapping_id | INTEGER | FOREIGN KEY | 使用的映射 ID |
| template_id | INTEGER | FOREIGN KEY | 使用的模板 ID |
| datasource_ids | JSON | DEFAULT [] | 使用的数据源 ID 列表（保留 JSON） |
| output_filename | VARCHAR(255) | NOT NULL | 输出文件名 |
| file_path | VARCHAR(500) | NOT NULL | 文件存储路径 |
| status | VARCHAR(50) | DEFAULT 'pending' | 状态 |
| error_message | TEXT | NULL | 错误信息 |
| create_time | DATETIME | DEFAULT CURRENT_TIMESTAMP | 生成时间 |

**外键约束**:
```sql
FOREIGN KEY (mapping_id) REFERENCES mappings(id) ON DELETE SET NULL
FOREIGN KEY (template_id) REFERENCES templates(id) ON DELETE SET NULL
```

---

## 3. 关系说明

### 3.1 Template ↔ Mapping

**关系**: 1:N（一对多）

**说明**: 
- 一个模板可以被多个映射配置使用
- 删除模板时，级联删除所有关联的映射

```sql
-- 查询示例：获取模板的所有映射
SELECT m.* FROM mappings m
WHERE m.template_id = :template_id;
```

---

### 3.2 Mapping ↔ DataSource

**关系**: M:N（多对多）

**说明**: 
- 一个映射可以使用多个数据源
- 一个数据源可以被多个映射使用
- 通过 `MappingDataSource` 关联表实现
- 支持数据源排序（order 字段）

```sql
-- 查询示例：获取映射的所有数据源（按顺序）
SELECT d.* FROM datasources d
INNER JOIN mapping_datasources md ON d.id = md.datasource_id
WHERE md.mapping_id = :mapping_id
ORDER BY md."order" ASC;

-- 查询示例：获取使用某数据源的所有映射
SELECT m.* FROM mappings m
INNER JOIN mapping_datasources md ON m.id = md.mapping_id
WHERE md.datasource_id = :datasource_id;
```

---

### 3.3 Mapping ↔ MappingChart

**关系**: 1:N（一对多）

**说明**: 
- 一个映射可以有多个图表配置
- 图表配置作为子实体独立存储
- 删除映射时，级联删除所有图表配置

```sql
-- 查询示例：获取映射的所有图表
SELECT * FROM mapping_charts
WHERE mapping_id = :mapping_id;
```

---

## 4. 与旧版本对比

### 4.1 变化总结

| 表名 | 变更类型 | 变更内容 |
|------|----------|----------|
| mappings | 删除列 | 删除 `datasource_ids` (JSON) |
| mappings | 删除列 | 删除 `charts` (JSON) |
| mapping_datasources | 新增表 | 映射 - 数据源关联表 |
| mapping_charts | 新增表 | 图表配置表 |

### 4.2 向后兼容性

通过 SQLAlchemy 的 property 保持向后兼容：

```python
class Mapping(Base):
    # 新关系
    datasource_links = relationship("MappingDataSource", ...)
    chart_configs = relationship("MappingChart", ...)
    
    # 向后兼容的 property
    @property
    def datasource_ids(self):
        return [link.datasource_id for link in self.datasource_links]
    
    @property
    def charts(self):
        return [chart.chart_config for chart in self.chart_configs]
```

---

## 5. 索引策略

### 5.1 现有索引

```sql
-- 主键索引（自动创建）
PRIMARY KEY (id)

-- 外键索引（建议创建）
CREATE INDEX idx_mappings_template_id ON mappings(template_id);
CREATE INDEX idx_mapping_datasources_mapping_id ON mapping_datasources(mapping_id);
CREATE INDEX idx_mapping_datasources_datasource_id ON mapping_datasources(datasource_id);
CREATE INDEX idx_mapping_charts_mapping_id ON mapping_charts(mapping_id);
CREATE INDEX idx_document_history_mapping_id ON document_history(mapping_id);
```

### 5.2 查询优化索引

```sql
-- 常用查询字段
CREATE INDEX idx_mapping_charts_chart_id ON mapping_charts(chart_id);
CREATE INDEX idx_datasources_type ON datasources(type);
CREATE INDEX idx_templates_category ON templates(category);
```

---

## 6. 数据完整性约束

### 6.1 级联删除

```sql
-- Mapping → MappingDataSource: CASCADE
-- Mapping → MappingChart: CASCADE
-- Template → Mapping: CASCADE
-- DataSource → MappingDataSource: CASCADE
```

### 6.2 业务规则

1. **Mapping 必须关联 Template**
   - `template_id NOT NULL`

2. **MappingDataSource 必须同时存在 Mapping 和 DataSource**
   - 两个外键都是 `NOT NULL`

3. **图表 ID 在同一 Mapping 中必须唯一**
   - `UNIQUE (mapping_id, chart_id)`

4. **数据源在 Mapping 中不能重复**
   - `PRIMARY KEY (mapping_id, datasource_id)`

---

## 7. 示例查询

### 7.1 获取完整映射信息（含数据源和图表）

```sql
SELECT 
    m.id,
    m.name,
    m.template_id,
    t.name as template_name,
    GROUP_CONCAT(d.name) as datasource_names,
    (SELECT COUNT(*) FROM mapping_charts mc WHERE mc.mapping_id = m.id) as chart_count
FROM mappings m
LEFT JOIN mapping_datasources md ON m.id = md.mapping_id
LEFT JOIN datasources d ON md.datasource_id = d.id
LEFT JOIN templates t ON m.template_id = t.id
WHERE m.id = :mapping_id
GROUP BY m.id;
```

### 7.2 获取文档生成所需的所有数据

```sql
-- 模板信息
SELECT * FROM templates WHERE id = :template_id;

-- 数据源列表（按顺序）
SELECT d.* FROM datasources d
INNER JOIN mapping_datasources md ON d.id = md.datasource_id
WHERE md.mapping_id = :mapping_id
ORDER BY md."order";

-- 图表配置
SELECT chart_config FROM mapping_charts
WHERE mapping_id = :mapping_id;
```

---

## 8. 迁移路径

### 8.1 从 v1.0 迁移到 v2.0

详见 `phase-11-database-normalization.md` 中的迁移脚本。

### 8.2 回滚方案

```sql
-- 如果迁移失败，可以回滚到旧版本
-- 1. 从新表提取数据
-- 2. 重建旧 JSON 列
-- 3. 删除新表
-- 详见迁移脚本的 downgrade 函数
```

---

**文档版本**: v1.0  
**最后更新**: 2024-04-22  
**负责人**: TBD
