# Phase 13: 配置管理改进

**Milestone**: v1.1 架构改进  
**优先级**: P1  
**状态**: 🔄 进行中  
**预计工作量**: 1 天  
**负责人**: TBD  
**依赖**: 无

---

## 1. 目标与背景

### 1.1 问题陈述

当前 `config.py` 中存在硬编码的绝对路径：

```python
TEMPLATE_STORAGE_PATH: str = "/Volumes/data/word_templates"  # ❌ 硬编码
DATA_SOURCE_STORAGE_PATH: str = "/Volumes/data/word_datasources"  # ❌ 硬编码
WORD_OUTPUT_PATH: str = "/Volumes/data/word_output"  # ❌ 硬编码
```

**影响**:
- 在不同机器上无法运行
- 违反可移植性原则
- 部署到新环境需要修改代码

### 1.2 解决方案

使用相对于项目目录的路径：

```python
BASE_DIR = Path(__file__).parent.parent.parent  # 项目根目录
TEMPLATE_STORAGE_PATH: str = str(BASE_DIR / "templates")
WORD_OUTPUT_PATH: str = str(BASE_DIR / "output")
```

---

## 2. 任务分解

### 2.1: 审查所有硬编码路径

**任务 ID**: 13.1  
**工作量**: 0.1 天  
**输出**: 硬编码路径清单

**发现的问题路径**:
- `app/core/config.py`: 6 个硬编码绝对路径

**验收标准**:
- [ ] 列出所有硬编码路径
- [ ] 确认每个路径的用途

---

### 2.2: 更新 config.py 使用相对路径

**任务 ID**: 13.2  
**工作量**: 0.3 天  
**输出**: 更新的 `app/core/config.py`

**修改方案**:

```python
from pathlib import Path
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).parent.parent.parent.resolve()


class Settings(BaseSettings):
    APP_NAME: str = "Word Report Backend"
    VERSION: str = "1.0.0"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = True
    
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000"]
    
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    DATABASE_URL: str = "sqlite+aiosqlite:///./doccenter.db"
    
    TEMPLATE_STORAGE_PATH: str = str(BASE_DIR / "templates")
    DATA_SOURCE_STORAGE_PATH: str = str(BASE_DIR / "datasources")
    MAPPING_STORAGE_PATH: str = str(BASE_DIR / "mappings")
    CHART_STORAGE_PATH: str = str(BASE_DIR / "charts")
    WORD_OUTPUT_PATH: str = str(BASE_DIR / "output")
    WORD_HISTORY_PATH: str = str(BASE_DIR / "history")
    
    MAX_TEMPLATE_SIZE: int = 100 * 1024 * 1024
    CHART_DPI: int = 300
    
    def validate_settings(self):
        """验证配置有效性"""
        for path_key in [
            'TEMPLATE_STORAGE_PATH',
            'DATA_SOURCE_STORAGE_PATH',
            'MAPPING_STORAGE_PATH',
            'CHART_STORAGE_PATH',
            'WORD_OUTPUT_PATH',
            'WORD_HISTORY_PATH'
        ]:
            path = Path(getattr(self, path_key))
            path.mkdir(parents=True, exist_ok=True)
    
    class Config:
        env_file = ".env"
        case_sensitive = True
```

**验收标准**:
- [ ] 所有路径使用相对路径
- [ ] 使用 `pathlib.Path` 处理路径
- [ ] 代码可在不同机器上运行

---

### 2.3: 添加配置验证逻辑

**任务 ID**: 13.3  
**工作量**: 0.2 天  
**输出**: 配置验证方法

**实现**:

```python
def validate_settings(self):
    """验证配置有效性"""
    errors = []
    
    for path_key in [
        'TEMPLATE_STORAGE_PATH',
        'DATA_SOURCE_STORAGE_PATH',
        'MAPPING_STORAGE_PATH',
        'CHART_STORAGE_PATH',
        'WORD_OUTPUT_PATH',
        'WORD_HISTORY_PATH'
    ]:
        path = Path(getattr(self, path_key))
        if not path.exists():
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"无法创建目录 {path_key}: {e}")
    
    if errors:
        raise ValueError(f"配置验证失败：\n" + "\n".join(errors))
```

**验收标准**:
- [ ] 启动时验证目录存在性
- [ ] 自动创建不存在的目录
- [ ] 验证失败时给出明确错误信息

---

### 2.4: 更新 .env.example

**任务 ID**: 13.4  
**工作量**: 0.2 天  
**输出**: 更新的 `.env.example`

**内容**:

```env
APP_NAME=Word Report Backend
VERSION=1.0.0
HOST=0.0.0.0
PORT=8000
RELOAD=True
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite+aiosqlite:///./doccenter.db

# 存储路径（可选，使用默认值即可）
# TEMPLATE_STORAGE_PATH=./templates
# DATA_SOURCE_STORAGE_PATH=./datasources
# MAPPING_STORAGE_PATH=./mappings
# CHART_STORAGE_PATH=./charts
# WORD_OUTPUT_PATH=./output
# WORD_HISTORY_PATH=./history
```

**验收标准**:
- [ ] 包含所有必要配置项
- [ ] 存储路径使用注释说明
- [ ] 包含默认值说明

---

### 2.5: 编写配置迁移指南

**任务 ID**: 13.5  
**工作量**: 0.2 天  
**输出**: 配置迁移文档

**内容**:

```markdown
## 配置迁移指南

### 从 v1.0 升级到 v1.1

#### 变更说明
- 存储路径从绝对路径改为相对路径
- 默认使用项目目录下的子目录

#### 默认配置对照

| 配置项 | v1.0 默认值 | v1.1 默认值 |
|--------|-------------|-------------|
| TEMPLATE_STORAGE_PATH | /Volumes/data/word_templates | ./templates |
| DATA_SOURCE_STORAGE_PATH | /Volumes/data/word_datasources | ./datasources |
| WORD_OUTPUT_PATH | /Volumes/data/word_output | ./output |

#### 迁移步骤

1. **备份数据**（如有必要）
   ```bash
   cp -r /Volumes/data/word_templates ./templates_backup
   ```

2. **更新 .env 文件**
   - 如果使用默认配置，无需修改
   - 如需自定义路径，在 .env 中设置

3. **迁移数据文件**
   ```bash
   # 将旧目录的文件复制到新目录
   cp -r /Volumes/data/word_templates/* ./templates/
   ```

4. **重启服务**
   ```bash
   python main.py
   ```

#### 自定义路径（如需要）

```bash
# .env 文件中自定义
TEMPLATE_STORAGE_PATH=/custom/path/templates
WORD_OUTPUT_PATH=/custom/path/output
```
```

**验收标准**:
- [ ] 包含迁移步骤
- [ ] 包含默认配置对照表
- [ ] 说明如何自定义路径

---

## 3. 风险与缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| 旧数据路径不兼容 | 中 | 中 | 提供迁移指南 |
| 目录创建失败 | 低 | 中 | 验证逻辑 |
| 配置覆盖问题 | 低 | 低 | .env 优先级高于默认值 |

---

## 4. 验收标准

### 4.1 技术验收

- [ ] 无硬编码绝对路径
- [ ] 配置文件有默认值和验证
- [ ] 新环境部署开箱即用
- [ ] 所有 API 测试通过

### 4.2 文档

- [ ] .env.example 完整
- [ ] 配置迁移指南完成

---

## 5. 估算与时间线

| 任务 ID | 任务名称 | 估算工时 |
|--------|----------|----------|
| 13.1 | 审查所有硬编码路径 | 0.1 天 |
| 13.2 | 更新 config.py 使用相对路径 | 0.3 天 |
| 13.3 | 添加配置验证逻辑 | 0.2 天 |
| 13.4 | 更新 .env.example | 0.2 天 |
| 13.5 | 编写配置迁移指南 | 0.2 天 |
| **总计** | | **1 天** |