# Word 报告生成系统

> 模板驱动的自动化 Word 报告生成平台。上传 `.docx` 模板、配置数据源与字段映射，
> 自动生成含动态表格与图表的专业报告。

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Vue](https://img.shields.io/badge/Vue-3.4-42b883?logo=vuedotjs&logoColor=white)](https://vuejs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 关于本项目的开发方式

**本项目由 AI 编程代理（Codex / Claude Code）主导完成。**

采用 GSD（Goal-Structured Development）方法论：把交付目标拆成 Milestone → Phase → Task 三级，
每个 Phase 都有独立的计划文档（`PLAN`）与总结文档（`SUMMARY`），记录决策依据与执行结果。
项目内共沉淀 **16 个 Phase** 的完整计划与总结（见 `.planning/phases/`）。

| 环节 | 承担方 | 说明 |
|------|--------|------|
| 需求拆解与阶段拆分 | AI Agent | 从一句话需求生成 ROADMAP 与 Phase 计划 |
| 技术选型 | **人工** | 架构决策由人拍板，Agent 提供候选方案与权衡分析 |
| 编码实现 | AI Agent | 后端服务、数据模型、前端页面、迁移脚本 |
| 测试编写与调试 | AI Agent | pytest 用例生成 + 失败用例定位修复 |
| 文档维护 | AI Agent | README / API 文档 / SUMMARY 与代码同步更新 |
| 结果验收 | **人工** | 业务正确性判断与最终交付确认 |

### 这个方法带来的实际收益

- **一个人完成了原本需要 2-3 人两个月的交付量**，项目当前约 5900 行后端代码 + 21 个前端源码文件
- **决策全部留痕**：每个 Phase 的技术决策与理由都记录在 `SUMMARY` 文档中，可回溯
- **架构演进有迹可循**：Phase 11（数据库规范化）→ 12（服务层解耦）→ 14（测试框架）
  → 15（MinIO 集成）→ 16（图表动态绑定），每一步的迁移脚本与兼容方案均可查

### 人工必须介入的地方

这个项目也记录了 AI Agent 的实际能力边界，以下环节必须由人判断：

- **架构选型**：是否引入 Repository 层、数据库迁移策略、MinIO vs 本地存储的取舍
- **数据库规范化时机**：Phase 11 中 JSON 字段是否拆成关联表，涉及向后兼容判断
- **图表动态绑定方案**：动态/静态双模式兼容策略是 Phase 16 的关键决策
- **多数据库适配细节**：Oracle / Kingbase 驱动在各版本下的行为差异需实测确认

> 结论：AI Agent 能承担实现层的绝大部分工作，但架构决策与业务正确性判断仍是人的职责。
> 这套「人定方向、Agent 推进」的模式，是本项目能单人完成全栈交付的关键。

---

## 核心特性

- **多数据源支持**：单个模板可从多个数据源获取数据，实现数据分离和复用
- **智能字段映射**：支持模板变量与数据源字段的灵活映射，支持自动匹配
- **图表可视化**：支持 7 种图表类型（柱状图、折线图、饼图、环形图、组合图、堆叠图、散点图）
- **复杂表格**：支持合并单元格、背景色、边框样式等复杂表格格式
- **长文本替换**：支持执行摘要、分析报告等长文本内容的动态替换
- **批量操作**：支持模板、数据源、映射配置的批量删除
- **历史记录**：完整的文档生成历史记录，支持重新生成和下载

## 技术栈

| 层次 | 技术 |
|------|------|
| 后端框架 | FastAPI 0.109.2 |
| 文档引擎 | docxtpl 0.16.7 · python-docx 1.1.2 |
| 图表生成 | matplotlib 3.8.3 |
| 数据库 | PostgreSQL 16（开发/生产）· SQLite（测试） |
| 数据库适配 | Kingbase · PostgreSQL · MySQL · Oracle |
| ORM | SQLAlchemy 2.0.25 |
| 对象存储 | MinIO |
| 数据验证 | Pydantic 2.6.1 |
| 前端 | Vue 3.4 · Vite 5.2 · Element Plus 2.6 · Pinia 2.1 |
| E2E 测试 | Playwright 1.42 |

## 项目结构

```
docCenter/
├── .planning/                # GSD 计划库（intel + 各 Phase 的 PLAN/SUMMARY）
├── word-report-backend/      # FastAPI 后端（routers -> services -> repositories -> models）
├── word-report-generator/    # Vue 3 前端
├── parameter_library/        # 参数库
├── PROJECT.md                # 项目愿景与目标
├── ROADMAP.md                # 里程碑与 Phase 规划
└── test-cases.md             # 测试用例
```

---

## 目录

1. [系统概述](#系统概述)
2. [技术架构](#技术架构)
3. [环境要求](#环境要求)
4. [安装部署](#安装部署)
5. [快速开始](#快速开始)
6. [功能详解](#功能详解)
7. [API 接口文档](#api-接口文档)
8. [常见问题](#常见问题)
9. [最佳实践](#最佳实践)

---

## 系统概述

### 产品简介

Word 报告生成系统是一个基于模板的自动化文档生成平台。用户上传 Word 模板（.docx），配置数据源和字段映射关系，系统即可自动从多个数据源获取数据，生成包含动态内容、数据表格和可视化图表的专业 Word 报告。

### 核心特性

- **多数据源支持**：单个模板可从多个数据源获取数据，实现数据分离和复用
- **智能字段映射**：支持模板变量与数据源字段的灵活映射，支持自动匹配
- **图表可视化**：支持 7 种图表类型（柱状图、折线图、饼图、环形图、组合图、堆叠图、散点图）
- **复杂表格**：支持合并单元格、背景色、边框样式等复杂表格格式
- **长文本替换**：支持执行摘要、分析报告等长文本内容的动态替换
- **批量操作**：支持模板、数据源、映射配置的批量删除
- **历史记录**：完整的文档生成历史记录，支持重新生成和下载

### 应用场景

- 企业年度/季度经营分析报告
- 财务报表自动生成
- 市场调研报告
- 项目验收报告
- 客户分析报告
- 任何需要定期生成的标准化 Word 文档

---

## 技术架构

### 后端技术栈

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| Web 框架 | FastAPI | 0.109.2 | 高性能异步 API 框架 |
| 文档引擎 | docxtpl | 0.16.7 | Word 模板渲染（基于 Jinja2） |
| 文档处理 | python-docx | 1.1.2 | Word 文档创建和编辑 |
| 图表生成 | matplotlib | 3.8.3 | 数据可视化图表生成 |
| 数据库 | PostgreSQL 16 | - | 异步驱动 asyncpg |
| ORM | SQLAlchemy | 2.0.25 | 数据库 ORM 框架 |
| 对象存储 | MinIO | latest | 文件（模板/图表/输出文档）存储 |
| 数据验证 | Pydantic | 2.6.1 | 数据验证和序列化 |
| HTTP 客户端 | requests | 2.31.0 | HTTP API 调用 |
| 数据库驱动 | psycopg2-binary / pymysql / cx-Oracle | - | 多类型数据库数据源支持 |

### 前端技术栈

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| 框架 | Vue 3 | 3.4.21 | 渐进式 JavaScript 框架 |
| 构建工具 | Vite | 5.2.0 | 下一代前端构建工具 |
| UI 组件库 | Element Plus | 2.6.1 | Vue 3 组件库 |
| 状态管理 | Pinia | 2.1.7 | Vue 3 状态管理 |
| 路由 | Vue Router | 4.3.0 | 官方路由管理器 |
| HTTP 客户端 | Axios | 1.6.8 | HTTP 请求库 |
| 测试框架 | Playwright | 1.42.0 | E2E 测试工具 |

### 系统架构图

```
┌─────────────────────────────────────────────────────────┐
│                      用户浏览器                          │
│                   http://localhost:5173                  │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP/JSON
                     ▼
┌─────────────────────────────────────────────────────────┐
│                  FastAPI Backend                         │
│                   http://localhost:8000                  │
│  ┌──────────┬──────────┬──────────┬──────────────────┐  │
│  │  认证    │  模板    │  数据源  │   映射配置       │  │
│  │  Auth    │ Templates│DataSources│  Mappings      │  │
│  └──────────┴──────────┴──────────┴──────────────────┘  │
│  ┌──────────┬──────────┬──────────┬──────────────────┐  │
│  │  图表    │  文档    │  历史    │   数据服务       │  │
│  │  Charts  │Documents │ History  │   Services       │  │
│  └──────────┴──────────┴──────────┴──────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
         ┌────────────────────────┐     ┌────────────────────────┐
         │     PostgreSQL 16      │     │     MinIO 对象存储      │
         │   doccenter 数据库      │     │  - templates/          │
         │                        │     │  - charts/             │
         │                        │     │  - output/             │
         │                        │     │  - history/            │
         └────────────────────────┘     └────────────────────────┘
         
         ┌────────────────────────┐
         │    外部数据源            │
         │  - HTTP API            │
         │  - Kingbase/PostgreSQL │
         │  - MySQL/Oracle        │
         │  - 静态 JSON/表单       │
         └────────────────────────┘
```

---

## 环境要求

### 后端环境

- **操作系统**: macOS / Linux / Windows
- **Python 版本**: Python 3.10+
- **内存**: 最低 2GB，推荐 4GB+
- **磁盘空间**: 最低 500MB（不含生成的文档）

### 前端环境

- **Node.js 版本**: Node.js 18+
- **npm 版本**: npm 9+
- **浏览器**: Chrome 90+, Safari 14+, Firefox 88+

### 字体要求（图表中文支持）

**macOS**:
- PingFang SC（苹方，系统自带）
- Heiti SC（黑体，系统自带）
- STHeiti（华文黑体，系统自带）

**Windows**:
- SimHei（黑体）
- Microsoft YaHei（微软雅黑）
- Arial Unicode MS

**Linux**:
- 安装 `fonts-wqy-zenhei` 或 `fonts-wqy-microhei`
- 或手动安装中文字体到 `~/.local/share/fonts/`

---

## 安装部署

### 1. 克隆项目

```bash
git clone <repository-url>
cd docCenter
```

### 2. 外部服务（Docker）

```bash
# PostgreSQL 16
docker run -d --name postgresql \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=doccenter \
  -p 5432:5432 \
  postgres:16

# MinIO 对象存储
docker run -d --name minio-test \
  -e MINIO_ROOT_USER=minioadmin \
  -e MINIO_ROOT_PASSWORD=minioadmin \
  -p 9000:9000 -p 9001:9001 \
  -v minio_data:/data \
  minio/minio server /data
```

### 3. 后端安装

```bash
cd word-report-backend

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
# macOS/Linux
source venv/bin/activate
# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选，使用默认配置可跳过）
cp .env.example .env
# 编辑 .env 文件，修改数据库路径、存储路径等配置

# 启动服务
python main.py
```

服务启动成功后，访问 http://localhost:8000/api/health 验证。

### 4. 前端安装

```bash
cd word-report-generator

# 安装依赖
npm install

# 配置 API 地址（可选，默认 http://localhost:8000）
cp .env.example .env
# 编辑 .env 文件，修改 VITE_API_BASE_URL

# 开发模式
npm run dev

# 生产构建
npm run build

# 运行测试
npm run test:e2e
```

前端服务启动后，访问 http://localhost:5173。

### 5. 目录结构说明

```
docCenter/
├── word-report-backend/          # 后端服务
│   ├── app/
│   │   ├── core/                # 核心配置
│   │   ├── models.py            # 数据库模型
│   │   ├── routers/             # API 路由
│   │   │   ├── auth.py          # 认证接口
│   │   │   ├── templates.py     # 模板管理
│   │   │   ├── datasources.py   # 数据源管理
│   │   │   ├── mappings.py      # 映射配置（含图表配置）
│   │   │   ├── documents.py     # 文档生成
│   │   │   ├── history.py       # 历史记录
│   │   │   ├── charts.py        # 图表生成
│   │   │   └── databases.py     # 数据库数据源配置
│   │   ├── services/            # 业务服务层
│   │   ├── repositories/        # 数据访问层 (Repository 模式)
│   │   └── migrations/          # 数据库迁移脚本
│   ├── templates/               # 模板文件存储
│   ├── datasources/             # 数据源配置存储
│   ├── mappings/                # 映射配置存储
│   ├── charts/                  # 生成的图表
│   ├── output/                  # 生成的文档
│   ├── history/                 # 历史文档
│   ├── doccenter.db             # SQLite 数据库
│   ├── main.py                  # 入口文件
│   ├── requirements.txt         # Python 依赖
│   └── .env                     # 环境配置
│
├── word-report-generator/        # 前端应用
│   ├── src/
│   │   ├── api/                 # API 调用封装
│   │   ├── router/              # 路由配置
│   │   ├── stores/              # 状态管理
│   │   ├── views/               # 页面组件
│   │   │   ├── Login.vue        # 登录页
│   │   │   ├── Layout.vue       # 布局组件
│   │   │   ├── Template.vue     # 模板管理
│   │   │   ├── DataSource.vue   # 数据源管理
│   │   │   ├── Mapping.vue      # 参数映射
│   │   │   ├── Generate.vue     # 文档生成
│   │   │   └── History.vue      # 历史记录
│   │   └── utils/
│   │       └── request.js       # HTTP 请求封装
│   ├── tests/                   # E2E 测试
│   ├── package.json             # Node 依赖
│   └── .env                     # 环境配置
│
└── README.md                     # 项目说明
```

---

## 快速开始

### 步骤 1: 登录系统

1. 访问 http://localhost:5173
2. 使用默认账号登录：
   - 用户名：`admin`
   - 密码：`admin123`

### 步骤 2: 上传 Word 模板

1. 进入**模板管理**页面
2. 点击**上传模板**按钮
3. 填写模板名称和分类
4. 选择 `.docx` 格式文件（最大 100MB）
5. 点击**上传**

> **提示**: 模板中使用 `{{变量名}}` 格式定义占位符，例如 `{{report_title}}`、`{{revenue}}`。

### 步骤 3: 配置数据源

1. 进入**数据源管理**页面
2. 点击**新增数据源**
3. 选择数据源类型：
   - **HTTP API**: 从外部 API 获取数据
   - **静态 JSON**: 直接填写 JSON 数据
   - **表单输入**: 手动填写字段值
4. 填写配置信息
5. 点击**保存**

### 步骤 4: 创建字段映射

1. 进入**参数映射**页面
2. 点击**新增映射**
3. 选择模板（可多选数据源）
4. 系统自动显示模板变量和数据源字段
5. 配置映射关系：
   - 选择数据源（每个字段可来自不同数据源）
   - 选择对应的字段
6. 点击**自动匹配**可快速匹配同名字段
7. 保存映射配置

### 步骤 5: 生成文档

1. 进入**文档生成**页面
2. 选择映射配置
3. 可选：输入文档名称
4. 点击**生成文档**
5. 生成完成后点击**下载文档**

### 步骤 6: 查看历史记录

1. 进入**历史记录**页面
2. 查看历史生成记录
3. 支持操作：
   - 下载文档
   - 重新生成
   - 删除记录
   - 批量删除（勾选多条记录）
   - 搜索和筛选

---

## 功能详解

### 1. 模板管理

#### 上传模板

- **支持格式**: `.docx`
- **文件大小**: ≤ 100MB
- **变量格式**: `{{变量名}}`
- **自动识别**: 上传后自动识别模板中的所有变量

#### 模板变量命名规范

```
✅ 推荐:
{{report_title}}      # 下划线分隔小写字母
{{revenue_2024}}      # 包含数字
{{p1_name}}           # 简短前缀

❌ 避免:
{{Report Title}}      # 包含空格
{{收入}}              # 中文字符（可能兼容性问题）
{{revenue.2024}}      # 点号（用于嵌套访问）
```

#### 下载模板

点击模板列表中的**下载**按钮，可下载已上传的模板文件。

#### 删除模板

点击**删除**按钮，确认后删除模板及其关联文件。

---

### 2. 数据源管理

#### 数据源类型

##### (1) HTTP API

从外部 API 接口获取数据。

**配置项**:
- **接口 URL**: API 地址（必填）
- **请求方法**: GET / POST
- **请求头**: 自定义 Headers（JSON 格式）
- **请求参数**: URL 参数（JSON 格式）
- **请求体**: POST 请求体（JSON 格式）
- **超时时间**: 默认 30 秒

**示例**:
```json
{
  "url": "https://api.example.com/sales/2024",
  "method": "GET",
  "headers": {
    "Authorization": "Bearer xxx"
  },
  "params": {
    "region": "east"
  },
  "timeout": 30
}
```

##### (2) 静态 JSON

直接填写 JSON 数据，适用于固定数据。

**配置项**:
- **JSON 文本**: JSON 格式数据

**示例**:
```json
{
  "revenue": "1285000",
  "net_profit": "152000",
  "growth_rate": "18.3%"
}
```

##### (3) 表单输入

通过表单界面手动填写字段值。

**配置项**:
- **自定义字段**: 动态添加字段名和值

##### (4) 数据库查询

从 Kingbase / PostgreSQL / MySQL / Oracle 数据库执行 SQL 查询获取数据。

**配置项**:
- **数据库类型**: Kingbase / PostgreSQL / MySQL / Oracle
- **连接信息**: 主机、端口、数据库名、用户名、密码
- **SQL 查询**: SELECT 语句（支持 `:param_name` 参数占位符）
- **SQL 参数**: 定义参数名称、类型（string/integer/date）和默认值
- **运行时参数**: 生成文档时可动态输入参数值

**示例**:
```json
{
  "type": "kingbase",
  "config": {
    "host": "192.168.1.100",
    "port": "54321",
    "database": "report_db",
    "user": "reader",
    "password": "******",
    "sql": "SELECT month, revenue FROM sales WHERE year = :year",
    "params": [
      {"name": "year", "type": "integer", "default": "2024"}
    ]
  }
}
```

**支持的数据库**:
| 数据库 | 驱动 | 默认端口 |
|--------|------|----------|
| Kingbase (人大金仓) | psycopg2 (PostgreSQL 协议兼容) | 54321 |
| PostgreSQL | psycopg2 | 5432 |
| MySQL | pymysql | 3306 |
| Oracle | cx-Oracle | 1521 |

#### 测试数据源

点击数据源的**测试**按钮，验证数据源连通性和数据格式。

#### 编辑/删除数据源

支持修改数据源配置或删除数据源。

---

### 3. 参数映射

#### 多数据源支持

单个映射配置可选择**多个数据源**，每个字段可指定来自不同的数据源。

**使用场景**:
- 基础信息（公司名称、报告日期）来自一个数据源
- 财务数据（收入、利润）来自另一个数据源
- 运营数据（客户数、满意度）来自第三个数据源

#### 字段映射配置

1. **选择模板**: 显示模板中的所有变量
2. **选择数据源**: 可多选，显示所有选中数据源的字段
3. **映射关系**:
   - **模板变量**: 左侧显示
   - **数据源**: 下拉选择（从已选数据源中）
   - **数据源字段**: 右侧下拉选择

#### 自动匹配

点击**自动匹配**按钮，系统自动匹配同名字段（不区分大小写）。

**匹配规则**:
- 完全匹配：`revenue` = `revenue`
- 忽略大小写：`Revenue` = `revenue`
- 一次匹配一个数据源（按选择顺序）

#### 映射配置示例

```json
{
  "name": "年度报告映射",
  "template_id": 1,
  "datasource_ids": [1, 2, 3],
  "mappings": [
    {"datasource_id": 1, "source": "company_name", "target": "company_name"},
    {"datasource_id": 2, "source": "revenue", "target": "revenue"},
    {"datasource_id": 3, "source": "customer_count", "target": "customer_count"}
  ]
}
```

---

### 4. 文档生成

#### 生成流程

1. **选择映射配置**: 下拉框显示所有映射（含模板和数据源信息）
2. **预览数据**: 点击**预览数据**查看将要使用的数据
3. **输入文档名称**: 可选，默认使用映射名称
4. **生成文档**: 点击按钮，显示加载状态
5. **查看结果**: 显示生成结果卡片（文档名称、模板、数据源、文件大小、时间）
6. **下载文档**: 点击**下载文档**按钮

#### 图表生成

如果映射配置中包含图表，系统会自动生成并嵌入到文档中。

**支持的图表类型**:
| 类型 | 标识 | 说明 |
|------|------|------|
| 柱状图 | `bar` | 标准柱状对比图 |
| 折线图 | `line` | 趋势分析折线图 |
| 饼图 | `pie` | 占比分析 |
| 环形图 | `donut` | 使用 pie 类型实现 |
| 组合图 | `combo` | 柱状图 + 折线图组合 |
| 堆叠柱状图 | `stack` | 多系列堆叠展示 |
| 散点图 | `scatter` | 散点/气泡图 |
| 沉降历时曲线 | `settlement_duration` | 专业工程图表 — 地面沉降 |
| 水位历时曲线 | `waterlevel_duration` | 专业工程图表 — 地下水位 |
| 沉降水位对比图 | `settlement_waterlevel_comparison` | 专业工程图表 — 对比分析 |

**两种数据模式**:

##### 静态模式（传统方式）

直接在映射配置中填写 x/y 轴数据：

```json
{
  "id": "revenue_trend",
  "type": "line",
  "title": "收入趋势分析",
  "x_label": "月份",
  "y_label": "收入（万元）",
  "x_data": ["1 月", "2 月", "3 月"],
  "y_data": [18500, 19200, 20100]
}
```

##### 动态绑定模式（推荐）

选择数据源字段作为 x/y 轴，数据在生成文档时自动从数据源获取：

```json
{
  "id": "revenue_trend",
  "type": "line",
  "title": "收入趋势分析",
  "x_label": "月份",
  "y_label": "收入（万元）",
  "unit": "万元",
  "datasource_id": 1,
  "x_field": "month",
  "y_field": "revenue"
}
```

**数据流**: 选择数据源字段 → 保存到映射 → 生成文档时自动提取数据 → 生成图表

**模板中的图表占位符**:
```
CHART_PLACEHOLDER_{chart_id}
```

例如：`CHART_PLACEHOLDER_revenue_trend`

#### 生成失败处理

如果生成失败，系统会显示具体错误信息：
- 模板文件不存在
- 数据源请求失败
- 渲染模板失败（变量不匹配）
- 图表生成失败

---

### 5. 历史记录

#### 查看记录

表格显示所有生成记录，包含：
- ID
- 文档名称
- 模板
- 数据源
- 状态（成功/失败）
- 生成时间
- 文件大小

#### 搜索和筛选

- **搜索**: 按文档名称模糊搜索
- **筛选**: 按状态筛选（成功/失败）

#### 分页

支持分页浏览，可选每页数量：10/20/50/100。

#### 批量删除

1. 勾选需要删除的记录
2. 点击顶部的**批量删除**按钮
3. 确认删除

#### 重新生成

点击**重新生成**按钮，使用相同的映射配置重新生成文档。

---

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:8000`
- **认证方式**: Header 中添加 `Authorization: <token>`
- **数据格式**: JSON

### 认证接口

#### 登录

```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}

# Response
{
  "token": "wr_xxx",
  "user": {
    "id": 1,
    "username": "admin",
    "nickname": "管理员"
  }
}
```

#### 获取当前用户

```http
GET /api/auth/me
Authorization: <token>

# Response
{
  "id": 1,
  "username": "admin",
  "nickname": "管理员"
}
```

#### 退出登录

```http
POST /api/auth/logout
Authorization: <token>

# Response
{
  "message": "退出成功"
}
```

---

### 模板管理

#### 获取模板列表

```http
GET /api/templates/?page=1&page_size=10
Authorization: <token>

# Response
{
  "total": 5,
  "page": 1,
  "page_size": 10,
  "data": [
    {
      "id": 1,
      "name": "年度报告模板",
      "category": "报表",
      "file_name": "template.docx",
      "file_size": 37454,
      "variables": ["report_title", "revenue", "..."],
      "create_time": "2024-01-15 10:30:00"
    }
  ]
}
```

#### 获取模板详情

```http
GET /api/templates/{template_id}
Authorization: <token>
```

#### 上传模板

```http
POST /api/templates/
Authorization: <token>
Content-Type: multipart/form-data

name: 年度报告模板
category: 报表
file: <template.docx>
```

#### 下载模板

```http
GET /api/templates/{template_id}/download
Authorization: <token>
```

#### 获取模板变量

```http
GET /api/templates/{template_id}/variables
Authorization: <token>

# Response
{
  "variables": ["report_title", "revenue", "net_profit"]
}
```

#### 删除模板

```http
DELETE /api/templates/{template_id}
Authorization: <token>

# Response
{
  "message": "删除成功"
}
```

---

### 数据源管理

#### 获取数据源列表

```http
GET /api/datasources/?page=1&page_size=10
Authorization: <token>

# Response
{
  "total": 3,
  "page": 1,
  "page_size": 10,
  "data": [
    {
      "id": 1,
      "name": "财务数据源",
      "type": "json",
      "config": {...},
      "status": "unknown",
      "create_time": "2024-01-15 10:30:00"
    }
  ]
}
```

#### 获取数据源详情

```http
GET /api/datasources/{ds_id}
Authorization: <token>
```

#### 创建数据源

```http
POST /api/datasources/
Authorization: <token>
Content-Type: application/json

{
  "name": "财务数据源",
  "type": "json",
  "config": {
    "json_text": "{\"revenue\": \"1000000\"}"
  }
}
```

#### 更新数据源

```http
PUT /api/datasources/{ds_id}
Authorization: <token>
Content-Type: application/json

{
  "name": "新名称",
  "config": {...}
}
```

#### 测试数据源

```http
POST /api/datasources/test
Authorization: <token>
Content-Type: application/json

{
  "type": "json",
  "config": {...},
  "ds_id": 1
}

# Response
{
  "success": true,
  "message": "连接成功",
  "data": {...}
}
```

#### 删除数据源

```http
DELETE /api/datasources/{ds_id}
Authorization: <token>
```

---

### 参数映射

#### 获取映射列表

```http
GET /api/mappings/?page=1&page_size=10
Authorization: <token>

# Response
{
  "items": [
    {
      "id": 1,
      "name": "年度报告映射",
      "template_id": 1,
      "datasource_ids": [1, 2, 3],
      "mappings": [
        {
          "datasource_id": 1,
          "source": "company_name",
          "target": "company_name"
        }
      ],
      "charts": [...],
      "create_time": "2024-01-15 10:30:00"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 10
}
```

#### 获取映射详情

```http
GET /api/mappings/{mapping_id}
Authorization: <token>
```

#### 创建映射

```http
POST /api/mappings/
Authorization: <token>
Content-Type: application/json

{
  "name": "年度报告映射",
  "template_id": 1,
  "datasource_ids": [1, 2, 3],
  "mappings": [
    {"datasource_id": 1, "source": "company_name", "target": "company_name"},
    {"datasource_id": 2, "source": "revenue", "target": "revenue"}
  ],
  "charts": [
    {
      "id": "revenue_trend",
      "type": "line",
      "title": "收入趋势",
      "x_label": "月份",
      "y_label": "收入",
      "x_data": ["1 月", "2 月"],
      "y_data": [100, 200]
    }
  ]
}
```

#### 更新映射

```http
PUT /api/mappings/{mapping_id}
Authorization: <token>
Content-Type: application/json

{
  "name": "新名称",
  "mappings": [...]
}
```

#### 删除映射

```http
DELETE /api/mappings/{mapping_id}
Authorization: <token>
```

---

### 文档生成

#### 生成文档

```http
POST /api/documents/generate
Authorization: <token>
Content-Type: application/json

{
  "mapping_id": 1,
  "output_name": "2024 年度报告"
}

# Response
{
  "id": 1,
  "name": "2024 年度报告.docx",
  "template": "年度报告模板",
  "datasource": "财务数据源，运营数据源",
  "status": "成功",
  "file_path": "/path/to/file.docx",
  "download_url": "/api/documents/1/download",
  "file_size": "36.7KB",
  "create_time": "2024-01-15 10:30:00"
}
```

#### 预览数据

```http
GET /api/documents/preview?data_source_id=1
Authorization: <token>

# Response
{
  "columns": ["revenue", "net_profit"],
  "data": [
    {"revenue": "1000000", "net_profit": "150000"}
  ]
}
```

---

### 历史记录

#### 获取历史记录

```http
GET /api/documents/history?page=1&page_size=10&search=报告&status=成功
Authorization: <token>

# Response
{
  "total": 20,
  "page": 1,
  "page_size": 10,
  "data": [
    {
      "id": 1,
      "name": "2024 年度报告.docx",
      "template": "",
      "datasource": "",
      "status": "成功",
      "file_size": "36.7KB",
      "create_time": "2024-01-15 10:30:00"
    }
  ]
}
```

#### 获取历史记录详情

```http
GET /api/documents/history/{history_id}
Authorization: <token>
```

#### 下载历史文档

```http
GET /api/documents/{doc_id}/download
Authorization: <token>

# Response
文件下载（application/vnd.openxmlformats-officedocument.wordprocessingml.document）
```

#### 重新生成文档

```http
POST /api/documents/history/{history_id}/regenerate
Authorization: <token>

# Response
同生成文档接口
```

#### 删除历史记录

```http
DELETE /api/documents/history/{history_id}
Authorization: <token>

# Response
{
  "message": "删除成功"
}
```

---

### 图表生成

#### 生成图表

```http
POST /api/charts/generate
Authorization: <token>
Content-Type: application/json

{
  "charts": [
    {
      "type": "bar",
      "title": "销售对比",
      "x_label": "产品",
      "y_label": "销售额",
      "x_data": ["产品 A", "产品 B"],
      "y_data": [100, 200],
      "color_scheme": "default"
    }
  ]
}

# Response
{
  "results": [
    {
      "id": "abc123",
      "filename": "chart_abc123.png",
      "filepath": "/path/to/chart.png",
      "file_size": 80649,
      "url": "/api/charts/chart_abc123.png"
    }
  ]
}
```

#### 获取图表列表

```http
GET /api/charts/list
Authorization: <token>
```

#### 获取图表文件

```http
GET /api/charts/{filename}
Authorization: <token>

# Response
图片文件（image/png）
```

#### 删除图表

```http
DELETE /api/charts/{filename}
Authorization: <token>
```

---

## 常见问题

### 1. 启动失败

**问题**: 后端启动时报错 `Address already in use`

**解决**:
```bash
# 查找占用 8000 端口的进程
lsof -i :8000

# 杀死进程
kill -9 <PID>

# 重新启动
python main.py
```

---

### 2. 数据库写入失败

**问题**: `sqlite3.OperationalError: attempt to write a readonly database`

**解决**:
```bash
# 删除数据库文件（会丢失数据，先备份）
rm word-report-backend/doccenter.db

# 确保目录有写权限
chmod 755 word-report-backend/

# 重启后端，会自动创建数据库
python main.py
```

---

### 3. 图表中文显示为方框

**问题**: 生成的图表中中文显示为 □□□

**解决**:

**macOS**: 已自动配置 PingFang SC，无需额外操作。

**Windows**:
1. 确保系统安装了中文字体
2. 修改 `chart_service.py`，添加字体配置：
```python
rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
```

**Linux**:
```bash
# 安装中文字体
sudo apt-get install fonts-wqy-zenhei

# 或手动复制字体文件到 ~/.local/share/fonts/
# 然后刷新字体缓存
fc-cache -fv
```

---

### 4. 下载文档显示 [object Object]

**问题**: 下载的 Word 文档打开后显示 `[object Object]`

**原因**: 前端 axios 响应拦截器配置错误

**解决**: 已修复，确保 `src/utils/request.js` 中：
```javascript
service.interceptors.response.use(
  response => {
    if (response.config.responseType === 'blob') {
      return response.data  // 不是 return response
    }
    return response.data
  },
  // ...
)
```

---

### 5. 模板变量未替换

**问题**: 生成的文档中仍有 `{{variable}}` 占位符

**原因**:
1. 映射配置中缺少该变量的映射
2. 数据源中缺少对应的字段
3. 变量名拼写错误

**解决**:
1. 检查模板中的变量名
2. 检查映射配置是否包含所有变量
3. 检查数据源字段是否匹配

---

### 6. 多数据源映射混乱

**问题**: 多个数据源时，字段映射错乱

**解决**:
1. 确保每个映射项都指定了正确的 `datasource_id`
2. 检查数据源字段名是否与模板变量匹配
3. 使用**自动匹配**功能前，先选择所有需要的数据源

---

### 7. 图表未嵌入文档

**问题**: 生成的文档中图表位置显示 `CHART_PLACEHOLDER_xxx`

**原因**:
1. 图表配置中的 `id` 与占位符不匹配
2. 图表生成失败

**解决**:
1. 确保模板中的占位符格式正确：`CHART_PLACEHOLDER_{id}`
2. 检查图表配置中的 `id` 字段
3. 查看后端日志，确认图表生成是否成功

---

### 8. 前端页面网络错误

**问题**: 所有页面打开都报网络错误

**原因**:
1. 后端服务未启动
2. 前后端端口配置不匹配
3. 跨域配置问题

**解决**:
```bash
# 1. 检查后端是否运行
curl http://localhost:8000/api/health

# 2. 检查前端配置的 API 地址
cat word-report-generator/.env
# 应为：VITE_API_BASE_URL=http://localhost:8000

# 3. 重启服务
# 后端
cd word-report-backend && python main.py

# 前端
cd word-report-generator && npm run dev
```

---

## 最佳实践

### 1. 模板设计

**推荐**:
- ✅ 使用有意义的变量名：`revenue_2024` 而不是 `var1`
- ✅ 将长文本放在单独段落，便于替换
- ✅ 图表占位符单独成行，居中对齐
- ✅ 使用表格展示结构化数据
- ✅ 为复杂报表设计封面和目录

**避免**:
- ❌ 变量名包含空格或特殊字符
- ❌ 在同一行混合多个变量
- ❌ 使用中文作为变量名

---

### 2. 数据源组织

**推荐**:
- ✅ 按业务领域分离数据源（财务、运营、市场）
- ✅ 使用描述性名称：`财务数据_2024` 而不是 `数据源 1`
- ✅ 定期测试数据源连通性
- ✅ 为 HTTP API 配置合理的超时时间

**数据源分类示例**:
```
基础信息数据源     - 公司名称、报告期间、编制部门
财务指标数据源     - 收入、利润、毛利率
运营指标数据源     - 客户数、订单率、满意度
区域市场数据源     - 各区域销售数据
风险评估数据源     - 风险描述、概率、影响
战略建议数据源     - 长文本建议内容
```

---

### 3. 映射配置

**推荐**:
- ✅ 为不同报告类型创建独立映射
- ✅ 使用自动匹配功能快速初始化
- ✅ 为映射配置描述性名称
- ✅ 定期审查和更新映射关系

**映射命名示例**:
```
年度报告 - 完整映射
季度报告 - 精简映射
财务报表 - 专用映射
```

---

### 4. 图表设计

**推荐**:
- ✅ 选择合适的图表类型展示数据
  - 趋势分析 → 折线图
  - 构成分析 → 饼图/环形图
  - 对比分析 → 柱状图
  - 多维度 → 组合图
- ✅ 使用清晰的图表标题
- ✅ 合理设置 X/Y 轴标签
- ✅ 数据系列不超过 7 个（避免拥挤）

**图表类型选择**:
```
收入趋势（2020-2024）  → line（折线图）
利润构成分析          → pie（饼图）
成本结构              → donut（环形图）
业务板块对比          → bar（柱状图）
区域销售分布          → pie（饼图）
重点区域趋势          → line（折线图）
风险矩阵              → scatter（散点图）
```

---

### 5. 性能优化

**大数据量处理**:
- 避免在单个数据源中放置过大 JSON（建议 < 1MB）
- 对于大量数据，使用 HTTP API 从数据库动态获取
- 定期清理历史文档和图表文件

**并发处理**:
- 多个数据源会并行获取，总耗时取决于最慢的数据源
- 优化慢查询的 API 接口
- 为 HTTP API 配置合理的超时时间

---

### 6. 安全管理

**生产环境部署**:
- ✅ 修改默认登录密码
- ✅ 配置 HTTPS
- ✅ 限制上传文件大小
- ✅ 定期备份数据库
- ✅ 限制 API 访问频率
- ✅ 日志审计和监控

**数据安全**:
- 不要在数据源中存储敏感信息（密码、密钥）
- 使用环境变量管理配置
- 定期清理生成的文档文件

---

### 7. 测试验证

**生成前检查清单**:
- [ ] 模板已上传且变量识别正确
- [ ] 数据源已配置且测试通过
- [ ] 映射关系已配置且完整
- [ ] 图表配置已添加且 ID 匹配
- [ ] 预览数据确认无误

**生成后验证**:
- [ ] 文档内容完整
- [ ] 数据替换正确
- [ ] 图表已嵌入且显示正常
- [ ] 表格格式正确
- [ ] 长文本内容完整

---

## 附录

### A. 版本历史

- **v1.0.0** (2024-01): 初始版本发布
  - 基础模板管理
  - 单数据源映射
  - 文档生成功能
  - 历史记录管理

- **v1.1.0** (2024-04): 多数据源支持
  - 支持多数据源映射
  - 每字段独立数据源选择
  - 图表自动嵌入
  - 批量删除功能
  - 中文字体支持

- **v1.1.1** (2026-04): 架构改进
  - 数据库规范化：显式外键约束、复合主键、关联表
  - 服务层解耦：Repository 模式、Service 层重构
  - 配置管理：分离硬编码配置
  - 测试框架：pytest + pytest-asyncio，62 项测试
  - 数据库数据源支持：Kingbase/PostgreSQL/MySQL/Oracle
  - SQL 参数运行时动态输入
  - 图表数据动态绑定（数据源字段映射）
  - MinIO 对象存储集成
  - 后端数据库迁移：SQLite → PostgreSQL 16

### B. 故障排查

**日志位置**:
- 后端日志：终端输出或 `server.log`
- 前端日志：浏览器开发者工具 Console

**常用排查命令**:
```bash
# 检查后端进程
ps aux | grep "python main.py"

# 检查端口占用
lsof -i :8000

# 查看数据库内容
sqlite3 word-report-backend/doccenter.db ".tables"

# 测试 API 接口
curl http://localhost:8000/api/health
```

