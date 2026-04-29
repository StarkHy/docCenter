# 测试文档

## 运行测试

```bash
cd word-report-backend
source venv/bin/activate
python -m pytest tests/ -v
```

## 运行特定测试

```bash
# 只运行 Repository 测试
python -m pytest tests/repositories/ -v

# 只运行 Service 测试
python -m pytest tests/services/ -v

# 只运行 API 测试
python -m pytest tests/api/ -v
```

## 带覆盖率运行

```bash
python -m pytest tests/ --cov=app --cov-report=term-missing
```

## 测试结构

```
tests/
├── conftest.py          # pytest fixtures
├── models/              # 模型层测试
│   └── test_template.py
├── repositories/        # Repository 层测试
│   ├── test_template_repository.py
│   ├── test_datasource_repository.py
│   └── test_mapping_repository.py
├── services/            # Service 层测试
│   ├── test_template_service.py
│   ├── test_datasource_service.py
│   └── test_mapping_service.py
└── api/                 # API 层测试
    ├── test_auth.py
    └── test_datasource.py
```

## 测试标记

- `@pytest.mark.asyncio` - 异步测试
- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试