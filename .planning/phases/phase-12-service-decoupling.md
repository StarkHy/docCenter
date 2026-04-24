# Phase 12: 服务层解耦

**Milestone**: v1.1 架构改进  
**优先级**: P0  
**状态**: 🔄 进行中  
**预计工作量**: 2 天  
**负责人**: TBD  
**依赖**: Phase 11 ✅ (数据库模式规范化已完成)

---

## 1. 目标与背景

### 1.1 问题陈述

当前代码架构中，Service 层直接依赖 SQLAlchemy 和数据库模型，导致：

1. **耦合度过高**: Service 与数据库实现细节绑定
2. **难以测试**: 无法独立测试业务逻辑，需要真实数据库
3. **违反单一职责**: Service 同时处理业务逻辑和数据访问
4. **代码复用困难**: 数据访问逻辑分散在 Service 各处

**当前问题代码示例**:

```python
# ❌ 当前 DocumentGenerationService 中的问题
class DocumentGenerationService:
    async def generate_document(self, mapping_id: int, session: AsyncSession):
        # 直接使用 session 查询数据库
        mapping = await session.get(Mapping, mapping_id)
        template = await session.get(Template, template_id)
        # ... 混合业务逻辑和数据访问
```

### 1.2 解决方案

引入 **Repository 层**，实现关注点分离：

```
┌─────────────────────────────────────────┐
│              Router Layer               │  ← API 端点
├─────────────────────────────────────────┤
│             Service Layer               │  ← 业务逻辑
├─────────────────────────────────────────┤
│           Repository Layer              │  ← 数据访问 (新增)
├─────────────────────────────────────────┤
│          SQLAlchemy Models              │  ← 数据库模型
└─────────────────────────────────────────┘
```

**Repository 职责**:
- 封装所有数据库操作
- 提供面向对象的查询接口
- 返回业务对象（而非 SQLAlchemy 模型）
- 隔离 Service 层与数据库实现

---

## 2. 任务分解

### 2.1: 定义 Repository 接口

**任务 ID**: 12.1  
**工作量**: 0.25 天  
**输出**: `app/repositories/base.py`

**接口设计**:

```python
# app/repositories/base.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    """Repository 基础接口"""
    
    @abstractmethod
    async def get_by_id(self, id: int) -> Optional[T]:
        """根据 ID 获取实体"""
        pass
    
    @abstractmethod
    async def get_all(self) -> List[T]:
        """获取所有实体"""
        pass
    
    @abstractmethod
    async def add(self, entity: T) -> T:
        """添加实体"""
        pass
    
    @abstractmethod
    async def update(self, entity: T) -> T:
        """更新实体"""
        pass
    
    @abstractmethod
    async def delete(self, id: int) -> bool:
        """删除实体"""
        pass
```

**验收标准**:
- [ ] 定义泛型 BaseRepository 接口
- [ ] 包含 CRUD 基础方法
- [ ] 使用 async/await 异步接口
- [ ] 类型注解完整

---

### 2.2: 实现 TemplateRepository

**任务 ID**: 12.2  
**工作量**: 0.5 天  
**输出**: `app/repositories/template_repository.py`

**实现代码**:

```python
# app/repositories/template_repository.py
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Template
from app.repositories.base import BaseRepository

class TemplateRepository(BaseRepository[Template]):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: int) -> Optional[Template]:
        result = await self.session.execute(select(Template).where(Template.id == id))
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[Template]:
        result = await self.session.execute(select(Template))
        return list(result.scalars().all())
    
    async def add(self, template: Template) -> Template:
        self.session.add(template)
        await self.session.flush()
        await self.session.refresh(template)
        return template
    
    async def update(self, template: Template) -> Template:
        await self.session.flush()
        await self.session.refresh(template)
        return template
    
    async def delete(self, id: int) -> bool:
        template = await self.get_by_id(id)
        if not template:
            return False
        await self.session.delete(template)
        await self.session.flush()
        return True
    
    async def get_paginated(self, page: int, page_size: int) -> tuple[List[Template], int]:
        """分页查询"""
        count_result = await self.session.execute(select(func.count(Template.id)))
        total = count_result.scalar() or 0
        
        offset = (page - 1) * page_size
        result = await self.session.execute(select(Template).offset(offset).limit(page_size))
        templates = list(result.scalars().all())
        
        return templates, total
    
    async def get_by_name(self, name: str) -> Optional[Template]:
        result = await self.session.execute(select(Template).where(Template.name == name))
        return result.scalar_one_or_none()
```

**验收标准**:
- [ ] 实现所有 BaseRepository 接口方法
- [ ] 添加分页查询方法
- [ ] 添加按名称查询方法
- [ ] 类型注解完整
- [ ] 单元测试通过

---

### 2.3: 实现 DataSourceRepository

**任务 ID**: 12.3  
**工作量**: 0.5 天  
**输出**: `app/repositories/datasource_repository.py`

**实现代码**:

```python
# app/repositories/datasource_repository.py
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import DataSource
from app.repositories.base import BaseRepository

class DataSourceRepository(BaseRepository[DataSource]):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: int) -> Optional[DataSource]:
        result = await self.session.execute(select(DataSource).where(DataSource.id == id))
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[DataSource]:
        result = await self.session.execute(select(DataSource))
        return list(result.scalars().all())
    
    async def add(self, datasource: DataSource) -> DataSource:
        self.session.add(datasource)
        await self.session.flush()
        await self.session.refresh(datasource)
        return datasource
    
    async def update(self, datasource: DataSource) -> DataSource:
        await self.session.flush()
        await self.session.refresh(datasource)
        return datasource
    
    async def delete(self, id: int) -> bool:
        datasource = await self.get_by_id(id)
        if not datasource:
            return False
        await self.session.delete(datasource)
        await self.session.flush()
        return True
    
    async def get_by_type(self, ds_type: str) -> List[DataSource]:
        """按类型查询数据源"""
        result = await self.session.execute(
            select(DataSource).where(DataSource.type == ds_type)
        )
        return list(result.scalars().all())
    
    async def get_paginated(self, page: int, page_size: int) -> tuple[List[DataSource], int]:
        """分页查询"""
        count_result = await self.session.execute(select(func.count(DataSource.id)))
        total = count_result.scalar() or 0
        
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(DataSource).offset(offset).limit(page_size)
        )
        datasources = list(result.scalars().all())
        
        return datasources, total
```

**验收标准**:
- [ ] 实现所有 BaseRepository 接口方法
- [ ] 添加按类型查询方法
- [ ] 添加分页查询方法
- [ ] 类型注解完整

---

### 2.4: 实现 MappingRepository

**任务 ID**: 12.4  
**工作量**: 0.5 天  
**输出**: `app/repositories/mapping_repository.py`

**实现代码**:

```python
# app/repositories/mapping_repository.py
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Mapping, MappingDataSource, MappingChart
from app.repositories.base import BaseRepository

class MappingRepository(BaseRepository[Mapping]):
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, id: int, eager_load: bool = True) -> Optional[Mapping]:
        """根据 ID 获取，可选择预加载关联数据"""
        query = select(Mapping).where(Mapping.id == id)
        
        if eager_load:
            query = query.options(
                selectinload(Mapping.datasource_links),
                selectinload(Mapping.chart_configs)
            )
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(self, eager_load: bool = False) -> List[Mapping]:
        query = select(Mapping)
        if eager_load:
            query = query.options(
                selectinload(Mapping.datasource_links),
                selectinload(Mapping.chart_configs)
            )
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def add(self, mapping: Mapping) -> Mapping:
        self.session.add(mapping)
        await self.session.flush()
        await self.session.refresh(mapping)
        return mapping
    
    async def update(self, mapping: Mapping) -> Mapping:
        await self.session.flush()
        await self.session.refresh(mapping)
        return mapping
    
    async def delete(self, id: int) -> bool:
        mapping = await self.get_by_id(id)
        if not mapping:
            return False
        await self.session.delete(mapping)
        await self.session.flush()
        return True
    
    async def get_by_template(self, template_id: int) -> List[Mapping]:
        """根据模板 ID 查询映射配置"""
        result = await self.session.execute(
            select(Mapping).where(Mapping.template_id == template_id)
        )
        return list(result.scalars().all())
    
    async def get_paginated(self, page: int, page_size: int) -> tuple[List[Mapping], int]:
        count_result = await self.session.execute(select(func.count(Mapping.id)))
        total = count_result.scalar() or 0
        
        offset = (page - 1) * page_size
        result = await self.session.execute(
            select(Mapping).offset(offset).limit(page_size)
        )
        mappings = list(result.scalars().all())
        
        return mappings, total
    
    async def add_datasource_link(self, mapping_id: int, datasource_id: int, order: int = 0) -> MappingDataSource:
        """添加数据源关联"""
        link = MappingDataSource(
            mapping_id=mapping_id,
            datasource_id=datasource_id,
            order=order
        )
        self.session.add(link)
        await self.session.flush()
        return link
    
    async def clear_datasource_links(self, mapping_id: int):
        """清空数据源关联"""
        result = await self.session.execute(
            select(MappingDataSource).where(MappingDataSource.mapping_id == mapping_id)
        )
        links = result.scalars().all()
        for link in links:
            await self.session.delete(link)
        await self.session.flush()
    
    async def add_chart_config(self, mapping_id: int, chart_data: dict) -> MappingChart:
        """添加图表配置"""
        chart = MappingChart(
            mapping_id=mapping_id,
            chart_id=chart_data.get("id", f"chart_{len(chart_data)}"),
            chart_type=chart_data.get("type"),
            chart_title=chart_data.get("title"),
            chart_config=chart_data
        )
        self.session.add(chart)
        await self.session.flush()
        return chart
    
    async def clear_chart_configs(self, mapping_id: int):
        """清空图表配置"""
        result = await self.session.execute(
            select(MappingChart).where(MappingChart.mapping_id == mapping_id)
        )
        charts = result.scalars().all()
        for chart in charts:
            await self.session.delete(chart)
        await self.session.flush()
```

**验收标准**:
- [ ] 实现所有 BaseRepository 接口方法
- [ ] 支持预加载关联数据（selectinload）
- [ ] 提供关联表操作方法
- [ ] 类型注解完整

---

### 2.5: 重构 DocumentGenerationService

**任务 ID**: 12.5  
**工作量**: 0.5 天  
**输出**: 重构后的 `app/services/document_generation_service.py`

**重构后代码**:

```python
# app/services/document_generation_service.py
from typing import Optional, List, Dict, Any
from docxtpl import DocxTemplate
from docx.shared import Inches
from app.repositories.template_repository import TemplateRepository
from app.repositories.datasource_repository import DataSourceRepository
from app.repositories.mapping_repository import MappingRepository
from app.services.chart_service import chart_service

class DocumentGenerationService:
    def __init__(
        self,
        template_repo: TemplateRepository,
        datasource_repo: DataSourceRepository,
        mapping_repo: MappingRepository
    ):
        self.template_repo = template_repo
        self.datasource_repo = datasource_repo
        self.mapping_repo = mapping_repo
    
    async def generate_document(
        self,
        mapping_id: int,
        output_name: Optional[str] = None
    ) -> dict:
        # 通过 Repository 获取数据
        mapping = await self.mapping_repo.get_by_id(mapping_id, eager_load=True)
        if not mapping:
            raise ValueError("映射配置不存在")
        
        template = await self.template_repo.get_by_id(mapping.template_id)
        if not template:
            raise ValueError("模板不存在")
        
        # 获取数据源数据
        datasource_data = await self._fetch_multiple_datasources(mapping.datasource_ids)
        
        # 应用字段映射
        context = self._apply_field_mapping(datasource_data, mapping.mappings)
        
        # 生成图表
        if mapping.charts:
            chart_results = self._generate_charts(mapping.charts)
            for chart_result in chart_results:
                context[f"chart_{chart_result['id']}"] = chart_result['filepath']
        
        # 渲染文档
        doc = DocxTemplate(template.file_path)
        doc.render(context)
        
        # 保存文档...
        return self._save_document(doc, output_name)
```

**验收标准**:
- [ ] Service 不再直接依赖 SQLAlchemy
- [ ] 所有数据库操作通过 Repository 进行
- [ ] 业务逻辑与数据访问分离
- [ ] 单元测试可独立运行（Mock Repository）

---

### 2.6: 引入依赖注入容器

**任务 ID**: 12.6  
**工作量**: 0.25 天  
**输出**: `app/core/dependencies.py`

**实现代码**:

```python
# app/core/dependencies.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.template_repository import TemplateRepository
from app.repositories.datasource_repository import DataSourceRepository
from app.repositories.mapping_repository import MappingRepository
from app.services.template_service import TemplateService
from app.services.datasource_service import DataSourceService
from app.services.mapping_service import MappingService
from app.services.document_generation_service import DocumentGenerationService

class DependencyContainer:
    """依赖注入容器"""
    
    @staticmethod
    def get_template_repository(session: AsyncSession) -> TemplateRepository:
        return TemplateRepository(session)
    
    @staticmethod
    def get_datasource_repository(session: AsyncSession) -> DataSourceRepository:
        return DataSourceRepository(session)
    
    @staticmethod
    def get_mapping_repository(session: AsyncSession) -> MappingRepository:
        return MappingRepository(session)
    
    @staticmethod
    def get_document_generation_service(
        template_repo: TemplateRepository,
        datasource_repo: DataSourceRepository,
        mapping_repo: MappingRepository
    ) -> DocumentGenerationService:
        return DocumentGenerationService(
            template_repo=template_repo,
            datasource_repo=datasource_repo,
            mapping_repo=mapping_repo
        )
```

**在 Router 中使用**:

```python
# app/routers/documents.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import get_db
from app.core.dependencies import DependencyContainer

router = APIRouter()

@router.post("/generate")
async def generate_document(
    mapping_id: int,
    session: AsyncSession = Depends(get_db)
):
    template_repo = DependencyContainer.get_template_repository(session)
    datasource_repo = DependencyContainer.get_datasource_repository(session)
    mapping_repo = DependencyContainer.get_mapping_repository(session)
    
    service = DependencyContainer.get_document_generation_service(
        template_repo, datasource_repo, mapping_repo
    )
    
    return await service.generate_document(mapping_id)
```

**验收标准**:
- [ ] 创建依赖注入容器
- [ ] 所有 Service 通过容器获取依赖
- [ ] Router 使用容器注入依赖
- [ ] 支持 Mock 依赖进行测试

---

## 3. 目录结构

重构后的目录结构：

```
word-report-backend/app/
├── core/
│   ├── config.py
│   └── dependencies.py          # ← 新增：依赖注入容器
├── repositories/                 # ← 新增：Repository 层
│   ├── __init__.py
│   ├── base.py                  # BaseRepository 接口
│   ├── template_repository.py
│   ├── datasource_repository.py
│   └── mapping_repository.py
├── services/                     # Service 层（重构后）
│   ├── __init__.py
│   ├── template_service.py
│   ├── datasource_service.py
│   ├── mapping_service.py
│   ├── document_generation_service.py  # 重构
│   └── chart_service.py
├── routers/                      # Router 层
│   ├── __init__.py
│   ├── templates.py
│   ├── datasources.py
│   ├── mappings.py
│   ├── documents.py
│   ├── history.py
│   ├── charts.py
│   └── auth.py
├── models.py                     # SQLAlchemy 模型
└── main.py
```

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 重构引入 Bug | 中 | 高 | 保持向后兼容，充分测试 |
| 性能下降 | 低 | 中 | 使用 selectinload 预加载 |
| 代码量增加 | 高 | 低 | 合理分层，职责清晰 |
| 学习成本 | 低 | 低 | 编写文档和示例 |

---

## 5. 验收标准

### 5.1 技术验收

- [ ] 所有 Repository 实现完成
- [ ] Service 层不再直接依赖 SQLAlchemy
- [ ] 依赖注入容器工作正常
- [ ] 所有 API 测试通过
- [ ] 性能测试通过（响应时间无明显下降）

### 5.2 代码质量

- [ ] 代码审查通过
- [ ] 类型注解完整
- [ ] 遵循项目代码规范
- [ ] 关键函数有文档字符串
- [ ] 无循环依赖

### 5.3 文档

- [ ] 架构文档已更新
- [ ] API 文档保持不变（向后兼容）
- [ ] 添加 Repository 使用指南

---

## 6. 依赖关系

**前置依赖**: Phase 11 ✅ (数据库模式规范化)  
**后续依赖**: 
- Phase 14: 测试框架搭建（可独立编写 Repository 单元测试）

---

## 7. 估算与时间线

| 任务 ID | 任务名称 | 估算工时 | 开始日期 | 结束日期 |
|--------|----------|----------|----------|----------|
| 12.1 | 定义 Repository 接口 | 0.25 天 | TBD | TBD |
| 12.2 | 实现 TemplateRepository | 0.5 天 | TBD | TBD |
| 12.3 | 实现 DataSourceRepository | 0.5 天 | TBD | TBD |
| 12.4 | 实现 MappingRepository | 0.5 天 | TBD | TBD |
| 12.5 | 重构 DocumentGenerationService | 0.5 天 | TBD | TBD |
| 12.6 | 引入依赖注入容器 | 0.25 天 | TBD | TBD |
| **总计** | | **2.5 天** | | |

---

## 8. 备注

- 本 Phase 保持 API 向后兼容，前端无需修改
- Repository 层为 Phase 14 的单元测试提供便利
- 未来可轻松切换数据库实现（如从 SQLite 迁移到 PostgreSQL）
