# Phase 15: MinIO 对象存储集成

**Milestone**: v1.1 架构改进  
**优先级**: P0 🔴 最高  
**状态**: 🔄 进行中  
**预计工作量**: 2 天  
**负责人**: TBD  
**依赖**: Phase 11 ✅, Phase 12 ✅, Phase 13 ✅, Phase 14 ✅

---

## 1. 目标与背景

### 1.1 问题陈述

当前文件存储在本地文件系统：
- 文件存储在 `./templates/`, `./output/` 等本地目录
- 无法跨机器访问
- 不支持分布式部署
- 缺乏版本管理和备份

### 1.2 解决方案

集成 MinIO 对象存储：
- 所有文件存储到 MinIO（templates, charts, output, history）
- 使用统一的存储服务接口
- 支持分布式部署和跨机器访问

---

## 2. 任务分解

### 2.1: 安装 MinIO Python SDK

**任务 ID**: 15.1  
**工作量**: 0.1 天  
**输出**: 安装 `minio` 包

**依赖**:
```
pip install minio
```

---

### 2.2: 更新配置文件

**任务 ID**: 15.2  
**工作量**: 0.2 天  
**输出**: `app/core/config.py` 添加 MinIO 配置

**配置项**:
```python
MINIO_ENDPOINT: str = "localhost:9000"
MINIO_ACCESS_KEY: str = "minioadmin"
MINIO_SECRET_KEY: str = "minioadmin"
MINIO_BUCKET: str = "doccenter"
MINIO_SECURE: bool = False  # True for HTTPS
```

---

### 2.3: 创建 MinIO 存储服务

**任务 ID**: 15.3  
**工作量**: 0.5 天  
**输出**: `app/services/storage_service.py`

**接口设计**:
```python
class StorageService:
    async def upload_file(self, bucket: str, file_name: str, file_data: bytes) -> str:
        """上传文件，返回文件路径"""
        
    async def download_file(self, file_path: str) -> bytes:
        """下载文件"""
        
    async def delete_file(self, file_path: str) -> bool:
        """删除文件"""
        
    async def get_file_url(self, file_path: str, expires: int = 3600) -> str:
        """获取文件访问 URL"""
```

---

### 2.4: 修改 Template 存储逻辑

**任务 ID**: 15.4  
**工作量**: 0.3 天  
**输出**: `app/services/template_service.py`

**修改**:
- 上传模板到 MinIO 而非本地目录
- 文件路径存储为 MinIO 对象键

---

### 2.5: 修改 Chart 存储逻辑

**任务 ID**: 15.5  
**工作量**: 0.3 天  
**输出**: `app/services/chart_service.py`

**修改**:
- 生成的图表上传到 MinIO

---

### 2.6: 修改 Document 输出存储

**任务 ID**: 15.6  
**工作量**: 0.3 天  
**输出**: `app/services/document_generation_service.py`

**修改**:
- 生成的文档上传到 MinIO

---

### 2.7: 添加桶初始化

**任务 ID**: 15.7  
**工作量**: 0.1 天  
**输出**: 启动时自动创建桶

---

## 3. 目录结构

```
app/
├── services/
│   ├── storage_service.py    # MinIO 存储服务
│   ├── template_service.py  # 修改
│   ├── chart_service.py     # 修改
│   └── document_generation_service.py  # 修改
└── core/
    └── config.py            # 添加 MinIO 配置
```

---

## 4. 验收标准

- [ ] MinIO SDK 安装成功
- [ ] 连接本地 MinIO 服务器
- [ ] 文件上传到 MinIO
- [ ] 文件从 MinIO 下载
- [ ] 模板上传功能正常
- [ ] 图表生成正常
- [ ] 文档生成正常
- [ ] 服务启动无错误

---

## 5. 估算

| 任务 ID | 任务名称 | 估算工时 |
|--------|----------|----------|
| 15.1 | 安装 MinIO SDK | 0.1 天 |
| 15.2 | 更新配置 | 0.2 天 |
| 15.3 | 创建存储服务 | 0.5 天 |
| 15.4 | 修改 Template 逻辑 | 0.3 天 |
| 15.5 | 修改 Chart 逻辑 | 0.3 天 |
| 15.6 | 修改 Document 逻辑 | 0.3 天 |
| 15.7 | 桶初始化 | 0.1 天 |
| **总计** | | **1.8 天** |