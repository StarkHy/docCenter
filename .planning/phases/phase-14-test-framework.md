# Phase 14: 测试框架搭建

**Milestone**: v1.1 架构改进  
**优先级**: P0  
**状态**: 🔄 进行中  
**预计工作量**: 3 天  
**负责人**: TBD  
**依赖**: Phase 11 ✅, Phase 12 ✅, Phase 13 ✅

---

## 1. 目标与背景

### 1.1 问题陈述

当前项目缺少测试框架：
- ❌ 无单元测试
- ❌ 无集成测试
- ❌ 无法验证代码正确性
- ❌ 重构风险高

### 1.2 解决方案

搭建完整的测试金字塔：

```
       ┌─────────────┐
       │  API 测试   │  ← 关键端点测试
       ├─────────────┤
       │ Service 测试 │  ← 业务逻辑测试
       ├─────────────┤
       │ Repo 测试   │  ← 数据访问测试
       ├─────────────┤
       │ Model 测试  │  ← 模型层测试
       └─────────────┘
```

**目标指标**:
- 单元测试覆盖率 >= 30%
- 关键业务逻辑有测试覆盖
- CI 自动运行测试

---

## 2. 任务分解

### 2.1: 配置 pytest 和测试工具

**任务 ID**: 14.1  
**工作量**: 0.3 天  
**输出**: pytest 配置 + 依赖

**依赖安装**:
```bash
pip install pytest pytest-asyncio httpx pytest-cov
```

**pytest.ini 配置**:
```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

**验收标准**:
- [ ] pytest 可运行
- [ ] asyncio 测试支持
- [ ] 覆盖率报告生成

---

### 2.2: 创建测试数据库 fixture

**任务 ID**: 14.2  
**工作量**: 0.4 天  
**输出**: `tests/conftest.py`

**实现**:
```python
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.models import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture(scope="function")
async def test_session(test_engine):
    async with AsyncSession(test_engine) as session:
        yield session
        await session.rollback()
```

**验收标准**:
- [ ] 每个测试使用独立的数据库
- [ ] 测试后自动清理
- [ ] 支持 async/await

---

### 2.3: 编写模型层测试

**任务 ID**: 14.3  
**工作量**: 0.5 天  
**输出**: `tests/models/`

**测试覆盖**:
- Template 模型 CRUD
- DataSource 模型 CRUD
- Mapping 模型 + 关联表
- DocumentHistory 模型

**验收标准**:
- [ ] 4 个模型测试文件
- [ ] 基本 CRUD 操作测试
- [ ] 关系测试（Mapping ↔ MappingDataSource）

---

### 2.4: 编写 Repository 层测试

**任务 ID**: 14.4  
**工作量**: 0.5 天  
**输出**: `tests/repositories/`

**测试覆盖**:
- TemplateRepository
- DataSourceRepository
- MappingRepository

**验收标准**:
- [ ] 3 个 Repository 测试文件
- [ ] 使用 Mock 或内存数据库
- [ ] 测试分页查询

---

### 2.5: 编写 Service 层测试

**任务 ID**: 14.5  
**工作量**: 0.5 天  
**输出**: `tests/services/`

**测试覆盖**:
- TemplateService
- MappingService
- DocumentGenerationService（核心逻辑）

**验收标准**:
- [ ] 3 个 Service 测试文件
- [ ] Mock 外部依赖
- [ ] 测试核心业务逻辑

---

### 2.6: 编写 API 层测试

**任务 ID**: 14.6  
**工作量**: 0.5 天  
**输出**: `tests/api/`

**测试覆盖**:
- 认证端点
- 模板 CRUD 端点
- 文档生成端点

**实现**:
```python
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_health():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
```

**验收标准**:
- [ ] API 端点测试
- [ ] 认证测试
- [ ] 错误处理测试

---

### 2.7: 配置 CI 测试运行

**任务 ID**: 14.7  
**工作量**: 0.3 天  
**输出**: GitHub Actions 配置

**.github/workflows/test.yml**:
```yaml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-asyncio httpx
      - name: Run tests
        run: pytest --cov=app tests/
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

**验收标准**:
- [ ] GitHub Actions 配置
- [ ] 自动运行测试
- [ ] 覆盖率报告

---

## 3. 验收标准

### 3.1 技术验收

- [ ] pytest 配置完成
- [ ] 测试数据库 fixture 可用
- [ ] 模型层测试通过
- [ ] Repository 层测试通过
- [ ] Service 层测试通过
- [ ] API 层测试通过

### 3.2 覆盖率要求

- [ ] 单元测试覆盖率 >= 30%
- [ ] 关键业务逻辑有测试覆盖

### 3.3 CI/CD

- [ ] GitHub Actions 配置完成
- [ ] 测试自动运行

---

## 4. 估算与时间线

| 任务 ID | 任务名称 | 估算工时 |
|--------|----------|----------|
| 14.1 | 配置 pytest 和测试工具 | 0.3 天 |
| 14.2 | 创建测试数据库 fixture | 0.4 天 |
| 14.3 | 编写模型层测试 | 0.5 天 |
| 14.4 | 编写 Repository 层测试 | 0.5 天 |
| 14.5 | 编写 Service 层测试 | 0.5 天 |
| 14.6 | 编写 API 层测试 | 0.5 天 |
| 14.7 | 配置 CI 测试运行 | 0.3 天 |
| **总计** | | **3 天** |