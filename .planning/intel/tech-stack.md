# 技术栈详细文档 - Word 报告生成系统

本文件对系统使用的技术栈、架构决策、组件关系及当前状态进行详细说明，帮助新成员快速了解现状与设计取舍。

## 1. 总览
- 目标：提供一个清晰、可扩展的技术蓝图，覆盖后端、前端、模板生成、数据源与部署运维等方面。
- 现状重点：后端基于 FastAPI + SQLAlchemy + PostgreSQL，前端基于 Vue 3 + Vite + Element Plus + Pinia。

## 2. 后端技术栈

### 当前技术栈（生产）

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| Web 框架 | FastAPI | 0.109.2 | 高性能异步 API 框架 |
| ORM | SQLAlchemy | 2.0.25 | 异步 ORM (asyncpg) |
| 数据库 | PostgreSQL | 16 | 异步驱动 asyncpg |
| 文档引擎 | docxtpl | 0.16.7 | Word 模板渲染（基于 Jinja2） |
| 文档处理 | python-docx | 1.1.2 | Word 文档创建和编辑 |
| 图表生成 | matplotlib | 3.8.3 | 数据可视化图表生成 |
| 数据验证 | Pydantic | 2.6.1 | 数据验证和序列化 |
| HTTP 客户端 | requests | 2.31.0 | HTTP API 调用 |
| 对象存储 | MinIO | latest | 文件（模板/图表/输出文档）存储 |
| 数据库驱动 | psycopg2-binary / pymysql / cx-Oracle | - | 多类型数据库数据源支持 |

### 数据库数据源支持

系统作为数据源连接器，支持从以下数据库查询数据：

| 数据库类型 | 驱动 | 说明 |
|-----------|------|------|
| Kingbase | psycopg2 (兼容 PostgreSQL 协议) | 人大金仓数据库 |
| PostgreSQL | psycopg2 | 标准 PostgreSQL |
| MySQL | pymysql | 标准 MySQL |
| Oracle | cx-Oracle | Oracle 数据库 |

### 架构分层

```
API 路由层 (routers/)
    ↕
Service 业务层 (services/)
    ↕
Repository 数据访问层 (repositories/)
    ↕
数据库模型层 (models.py)
```

- **Repository 模式**: 每个核心实体都有对应的 Repository 类，封装所有数据库查询逻辑，便于单元测试（支持 in-memory SQLite 测试）
- **Service 层**: 业务逻辑封装，通过构造器注入 Repository 依赖

## 3. 前端技术栈

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 框架 | Vue 3 | 3.4.21 | 渐进式 JavaScript 框架 |
| 构建工具 | Vite | 5.4.21 | 下一代前端构建工具 |
| UI 组件库 | Element Plus | 2.6.1 | Vue 3 组件库 |
| 状态管理 | Pinia | 2.1.7 | Vue 3 状态管理 |
| 路由 | Vue Router | 4.3.0 | 官方路由管理器 |
| HTTP 客户端 | Axios | 1.6.8 | HTTP 请求库 |

## 4. 核心功能

### 模板管理
- 上传/下载/删除 Word 模板 (.docx)
- 自动识别模板中的 Jinja2 变量 `{{变量名}}`
- 文件存储：MinIO 对象存储 + 本地缓存

### 数据源管理
- **HTTP API**: 从外部 REST API 获取数据（支持 GET/POST，自定义 Headers/Params/Body）
- **静态 JSON**: 直接填写 JSON 数据
- **表单输入**: 手动填写字段值
- **数据库查询**: 支持 Kingbase/PostgreSQL/MySQL/Oracle 数据库 SQL 查询
  - SQL 参数支持（`:param_name` 占位符替换）
  - 结果自动转换为 JSON
  - 运行时参数动态输入

### 字段映射
- 多数据源支持：单个映射配置可指定多个数据源
- 每字段独立选择数据源
- 自动匹配（忽略大小写）
- 点号路径支持嵌套字段访问（如 `data.items.0.name`）

### 文档生成
- 模板引擎渲染（docxtpl/Jinja2）
- 图表自动生成并嵌入 Word 文档
- 图表支持 7 种类型 + 3 种专业工程图表
- 图表数据支持动态绑定（从数据源字段映射）

### 图表系统
- **静态模式**: 在映射配置中直接填写 x_data/y_data
- **动态模式**: 选择数据源字段作为 x/y 轴，生成时自动从数据源提取数据
- 标准图表: 柱状图、折线图、饼图、环形图、组合图、堆叠图、散点图
- 专业图表: 沉降历时曲线、地下水位历时曲线、分层标对比图

### 历史记录
- 文档生成历史完整可追溯
- 支持重新生成、下载、删除（含批量删除）
- 搜索和状态筛选

## 5. 数据库设计

### 当前状态（v1.1 规范化后）
- 数据库：PostgreSQL（开发/生产），SQLite（测试）
- 表结构经过规范化重构（Phase 11）
- 核心表使用显式外键约束和复合主键

### 核心实体关系
```
Template (1) ──→ Mapping (N) ──→ DataSource (M:N via MappingDataSource)
                       │
                       └──→ MappingChart (1:N)
```

### 表结构
| 表名 | 说明 |
|------|------|
| templates | 模板信息（文件路径、变量列表） |
| datasources | 数据源配置（类型、连接信息） |
| mappings | 映射配置（关联模板和数据源） |
| mapping_datasources | 映射-数据源关联表（复合主键） |
| mapping_charts | 映射图表配置表 |
| document_history | 文档生成历史记录 |
| report_parameters | 月报参数表 |
| databases | 数据库连接配置 |

## 6. 存储架构

```
文件存储: MinIO (对象存储)
  ├── templates/    — 上传的 Word 模板
  ├── charts/       — 生成的图表图片
  ├── output/       — 生成的 Word 文档
  └── history/      — 历史文档

本地缓存 (可选):
  ├── templates/    — 模板文件本地副本
  ├── charts/       — 图表文件本地缓存
  └── output/       — 输出文档本地副本
```

## 7. 测试

| 层级 | 工具 | 状态 |
|------|------|------|
| Repository 单元测试 | pytest + pytest-asyncio | ✅ 26 测试（3 个 Repository） |
| Service 层测试 | pytest | ✅ 已覆盖 |
| API 层测试 | pytest + httpx | ✅ 已覆盖 |
| 模型层测试 | pytest | ✅ 已覆盖 |
| **总计** | | **62 测试通过** |

测试策略：
- Repository 测试使用 in-memory SQLite 保证隔离性
- API 测试使用 TestClient
- Service 测试通过构造器注入 mock Repository

## 8. 配置与部署

- 配置源：`.env` 文件 + 环境变量
- 数据库：开发 PostgreSQL，测试 SQLite
- 对象存储：MinIO（Docker）
- 安全：JWT 认证（Token 鉴权）
- 开发环境：`python main.py`（热重载）

### Docker 依赖
- PostgreSQL 16 容器（端口 5432）
- MinIO 容器（端口 9000 S3 API / 9001 控制台）

## 9. 架构原则与模式

- **分层设计**：表现层（routers）→ 服务层（services）→ 数据访问层（repositories）→ 模型层（models）
- **Repository 模式**：隔离数据访问逻辑，便于单元测试
- **依赖注入**：通过构造器注入解耦组件
- **动态/静态双模式**：图表等组件支持配置驱动和数据驱动两种模式
- **兼容性优先**：新功能保留旧模式的向后兼容

## 10. 版本演进

| 版本 | 完成日期 | 内容 |
|------|----------|------|
| v1.0 | 2024-04 | 初始版本：核心 CRUD、文档生成 |
| v1.1 | 2026-04 | 架构改进：数据库规范化、服务解耦、测试框架、数据库数据源、图表动态绑定 |
| v1.2 | 待规划 | 功能增强：批量操作、映射增强、历史审计 |
