# Phase 11: 数据库模式规范化

**Milestone**: v1.1 架构改进  
**优先级**: P0  
**状态**: 📋 待开始  
**预计工作量**: 3 天  
**负责人**: TBD

---

## 1. 目标与背景

### 1.1 问题陈述

当前数据库设计存在严重问题，违反数据库规范化原则：

```python
# 当前问题代码 (app/models.py)
class Mapping(Base):
    datasource_ids = Column(JSON, default=list)  # ❌ 违反第一范式
    charts = Column(JSON, default=list)          # ❌ 子实体用 JSON 存储
```

**影响**:
- 无法进行外键约束，数据完整性无法保证
- 无法查询"哪些映射使用了某个数据源"
- 无法级联删除（删除数据源时无法自动清理关联）
- 查询性能差（需要解析 JSON）
- 不符合数据库设计规范

### 1.2 解决方案

创建规范化的关联表，使用外键约束：

```python
# 新的关联表
class MappingDataSource(Base):
    __tablename__ = 'mapping_datasources'
    mapping_id = Column(Integer, ForeignKey('mappings.id'), primary_key=True)
    datasource_id = Column(Integer, ForeignKey('datasources.id'), primary_key=True)
    order = Column(Integer, default=0)  # 支持数据源排序

class MappingChart(Base):
    __tablename__ = 'mapping_charts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    mapping_id = Column(Integer, ForeignKey('mappings.id'), nullable=False)
    chart_id = Column(String(100), nullable=False)  # 图表唯一标识
    chart_type = Column(String(50))
    chart_config = Column(JSON)  # 图表配置可以是 JSON
```

---

## 2. 任务分解

### 2.1 设计新的数据库 ERD

**任务 ID**: 11.1  
**工作量**: 0.5 天  
**输出**: ERD 图表文件

**验收标准**:
- [ ] 包含所有实体（Template, DataSource, Mapping, DocumentHistory）
- [ ] 包含所有关联表（MappingDataSource, MappingChart）
- [ ] 标注所有外键关系
- [ ] 标注字段类型和约束

---

### 2.2 创建关联表模型

**任务 ID**: 11.2  
**工作量**: 0.5 天  
**输出**: 新的模型文件

**实现代码**:

```python
# app/models.py - 新增
class MappingDataSource(Base):
    __tablename__ = 'mapping_datasources'
    
    mapping_id = Column(Integer, ForeignKey('mappings.id', ondelete='CASCADE'), primary_key=True)
    datasource_id = Column(Integer, ForeignKey('datasources.id', ondelete='CASCADE'), primary_key=True)
    order = Column(Integer, default=0, nullable=False)
    
    # 关系
    datasource = relationship("DataSource")

class MappingChart(Base):
    __tablename__ = 'mapping_charts'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    mapping_id = Column(Integer, ForeignKey('mappings.id', ondelete='CASCADE'), nullable=False)
    chart_id = Column(String(100), nullable=False, index=True)
    chart_type = Column(String(50))
    chart_title = Column(String(255))
    chart_config = Column(JSON, default=dict)
    
    # 唯一约束：同一个 mapping 中 chart_id 唯一
    __table_args__ = (
        UniqueConstraint('mapping_id', 'chart_id', name='uq_mapping_chart'),
    )
```

**验收标准**:
- [ ] 模型文件创建完成
- [ ] 外键约束配置正确（包括 ondelete='CASCADE'）
- [ ] 索引和唯一约束配置正确
- [ ] 添加 relationship 方便查询

---

### 2.3 更新 Mapping 模型

**任务 ID**: 11.3  
**工作量**: 0.5 天  

**修改内容**:

```python
# app/models.py - 修改 Mapping 类
class Mapping(Base):
    # ... 现有字段保持不变 ...
    
    # 删除这些 JSON 字段
    # datasource_ids = Column(JSON, default=list)  # ❌ 删除
    # charts = Column(JSON, default=list)          # ❌ 删除
    
    # 添加关系
    datasource_links = relationship(
        "MappingDataSource",
        back_populates="mapping",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    chart_configs = relationship(
        "MappingChart",
        back_populates="mapping",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # 添加辅助方法保持向后兼容
    @property
    def datasource_ids(self):
        """保持向后兼容的 property"""
        return [link.datasource_id for link in self.datasource_links]
    
    @property
    def charts(self):
        """保持向后兼容的 property"""
        return [chart.chart_config for chart in self.chart_configs]
```

**验收标准**:
- [ ] JSON 字段已删除
- [ ] relationship 配置正确
- [ ] 向后兼容的 property 已添加
- [ ] 现有代码无需大幅修改

---

### 2.4 编写数据库迁移脚本

**任务 ID**: 11.4  
**工作量**: 1 天  
**输出**: 迁移脚本文件

**迁移步骤**:

```python
# app/migrations/migrate_to_v2.py
"""
迁移：JSON 字段 -> 关联表
版本：v1.1 -> v1.2
"""

import json
from sqlalchemy import text

async def migrate_upgrade(connection):
    """向上迁移"""
    # 1. 创建新表
    await connection.execute(text("""
        CREATE TABLE mapping_datasources (
            mapping_id INTEGER NOT NULL,
            datasource_id INTEGER NOT NULL,
            order INTEGER DEFAULT 0 NOT NULL,
            PRIMARY KEY (mapping_id, datasource_id),
            FOREIGN KEY (mapping_id) REFERENCES mappings(id) ON DELETE CASCADE,
            FOREIGN KEY (datasource_id) REFERENCES datasources(id) ON DELETE CASCADE
        )
    """))
    
    await connection.execute(text("""
        CREATE TABLE mapping_charts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mapping_id INTEGER NOT NULL,
            chart_id VARCHAR(100) NOT NULL,
            chart_type VARCHAR(50),
            chart_title VARCHAR(255),
            chart_config JSON,
            FOREIGN KEY (mapping_id) REFERENCES mappings(id) ON DELETE CASCADE,
            UNIQUE (mapping_id, chart_id)
        )
    """))
    
    # 2. 数据迁移：从 JSON 到新表
    # 获取所有 mappings
    result = await connection.execute(text("SELECT id, datasource_ids, charts FROM mappings"))
    mappings = result.fetchall()
    
    for mapping in mappings:
        if mapping.datasource_ids:
            datasource_ids = json.loads(mapping.datasource_ids)
            for idx, ds_id in enumerate(datasource_ids):
                await connection.execute(text("""
                    INSERT INTO mapping_datasources (mapping_id, datasource_id, "order")
                    VALUES (:mapping_id, :datasource_id, :order)
                """), {
                    "mapping_id": mapping.id,
                    "datasource_id": ds_id,
                    "order": idx
                })
        
        if mapping.charts:
            charts = json.loads(mapping.charts)
            for chart in charts:
                chart_id = chart.get('id', f'chart_{len(charts)}')
                await connection.execute(text("""
                    INSERT INTO mapping_charts (mapping_id, chart_id, chart_type, chart_title, chart_config)
                    VALUES (:mapping_id, :chart_id, :chart_type, :chart_title, :chart_config)
                """), {
                    "mapping_id": mapping.id,
                    "chart_id": chart_id,
                    "chart_type": chart.get('type'),
                    "chart_title": chart.get('title'),
                    "chart_config": json.dumps(chart)
                })
    
    # 3. 删除旧 JSON 列（SQLite 不支持 DROP COLUMN，需要重建表）
    # SQLite 特定处理...
    
    print("Migration completed successfully")

async def migrate_downgrade(connection):
    """向下回滚"""
    # 反向操作...
    pass
```

**验收标准**:
- [ ] 迁移脚本可执行
- [ ] 数据正确迁移
- [ ] 回滚脚本已测试
- [ ] 迁移有日志记录

---

### 2.5 更新 Repository 层代码

**任务 ID**: 11.5  
**工作量**: 1 天  

**需要更新的文件**:
- `app/services/mapping_service.py`
- `app/routers/mappings.py`
- `app/services/document_generation_service.py`

**修改示例**:

```python
# app/services/mapping_service.py

# ❌ 旧代码
async def create_mapping(mapping_data: dict, session: AsyncSession):
    mapping = Mapping(
        name=mapping_data['name'],
        template_id=mapping_data['template_id'],
        datasource_ids=mapping_data['datasource_ids'],  # JSON 列表
        charts=mapping_data['charts']
    )
    session.add(mapping)
    await session.commit()

# ✅ 新代码
async def create_mapping(mapping_data: dict, session: AsyncSession):
    mapping = Mapping(
        name=mapping_data['name'],
        template_id=mapping_data['template_id']
    )
    session.add(mapping)
    await session.flush()  # 获取 mapping.id
    
    # 添加关联数据源
    for idx, ds_id in enumerate(mapping_data['datasource_ids']):
        link = MappingDataSource(
            mapping_id=mapping.id,
            datasource_id=ds_id,
            order=idx
        )
        session.add(link)
    
    # 添加图表配置
    for chart in mapping_data.get('charts', []):
        chart_obj = MappingChart(
            mapping_id=mapping.id,
            chart_id=chart.get('id'),
            chart_type=chart.get('type'),
            chart_title=chart.get('title'),
            chart_config=chart
        )
        session.add(chart_obj)
    
    await session.commit()
```

**验收标准**:
- [ ] 所有 CRUD 操作已更新
- [ ] 查询性能未下降
- [ ] 向后兼容的 API 保持可用

---

### 2.6 数据迁移和验证

**任务 ID**: 11.6  
**工作量**: 0.5 天  

**验证步骤**:

1. **备份数据**
```bash
cp word-report-backend/doccenter.db word-report-backend/doccenter.db.backup
```

2. **运行迁移**
```bash
cd word-report-backend
python -m app.migrations.migrate_to_v2
```

3. **验证数据完整性**
```python
# 验证脚本
async def verify_migration():
    async with async_session() as session:
        # 检查 mappings 数量
        mappings_count = await session.count(Mapping)
        
        # 检查关联数据
        for mapping in await session.scalars(select(Mapping)):
            assert len(mapping.datasource_links) > 0 or len(mapping.chart_configs) == 0
            print(f"✓ Mapping {mapping.id}: {len(mapping.datasource_links)} datasources")
        
        print("✓ All data verified successfully")
```

**验收标准**:
- [ ] 所有数据成功迁移
- [ ] 外键约束生效
- [ ] 查询结果正确
- [ ] 性能测试通过

---

## 3. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 数据迁移失败 | 中 | 高 | 完整备份 + 回滚脚本 |
| 性能下降 | 低 | 中 | 添加索引 + 性能测试 |
| API 不兼容 | 中 | 高 | 保持向后兼容的 property |
| 迁移时间过长 | 低 | 低 | 分批迁移 + 进度日志 |

---

## 4. 验收标准

### 4.1 技术验收

- [ ] 新模型通过 SQLAlchemy 创建
- [ ] 数据库迁移脚本执行成功
- [ ] 现有数据成功迁移（100% 数据完整性）
- [ ] 所有 API 测试通过
- [ ] 回滚方案已验证

### 4.2 代码质量

- [ ] 代码审查通过
- [ ] 无硬编码
- [ ] 遵循项目代码规范
- [ ] 关键函数有文档字符串

### 4.3 文档

- [ ] 迁移文档已更新
- [ ] API 文档已更新
- [ ] 部署指南已更新

---

## 5. 依赖关系

**前置依赖**: 无  
**后续依赖**: 
- Phase 12: 服务层解耦（依赖本 Phase 的模型变更）
- Phase 14: 测试框架搭建（依赖本 Phase 的新模型）

---

## 6. 估算与时间线

| 任务 ID | 任务名称 | 估算工时 | 开始日期 | 结束日期 |
|--------|----------|----------|----------|----------|
| 11.1 | 设计 ERD | 0.5 天 | TBD | TBD |
| 11.2 | 创建关联表模型 | 0.5 天 | TBD | TBD |
| 11.3 | 更新 Mapping 模型 | 0.5 天 | TBD | TBD |
| 11.4 | 编写迁移脚本 | 1 天 | TBD | TBD |
| 11.5 | 更新 Repository 层 | 1 天 | TBD | TBD |
| 11.6 | 数据迁移验证 | 0.5 天 | TBD | TBD |
| **总计** | | **4 天** | | |

---

## 7. 备注

- 本 Phase 是 v1.1 里程碑的关键路径
- 需要充分测试后再部署到生产环境
- 建议先在开发环境验证 1 周
