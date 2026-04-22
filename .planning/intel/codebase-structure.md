# Word 报告生成系统 - 代码库结构设计

本文档描述代码库的总体结构、各模块职责、关键模型与约定，帮助团队成员快速定位并理解实现位置，降低新手入门成本。

## 1. 顶层结构概览
- backend/  - FastAPI + SQLAlchemy 后端服务
- frontend/ - Vue 3 + Vite 前端应用
- tests/    - 测试用例（单元/集成）
- .planning/ - 计划与智力投资文档
- templates/ - 存放 Word 模板文件（在实际实现中可挂载到模板服务）
- config/    - 配置文件模板（环境变量/ YAML/JSON）
- README.md  - 项目说明与快速上手指引（若存在）

> 注：以下结构描述偏向初始阶段的合理结构，后续会基于需求演变对目录进行调整。 

## 2. 后端结构（backend/）
- app/
  - main.py                启动应用、路由注册、中间件配置
  - config.py              配置加载与环境变量封装
  - api/
    - v1/
      - routers/            路由分组实现
      - endpoints/          具体端点实现（控制器/处理逻辑）
  - core/
    - security/             安全相关（鉴权、密码学工具等，后续扩展）
    - config.py             全局应用配置
  - models/                 SQLAlchemy 数据模型（ORM）
  - schemas/                Pydantic 模式（API 输入/输出）
  - repositories/           数据访问层，封装 ORM 操作
  - services/               业务逻辑层，协调数据源、模板、映射等
  - templates/              模板模板（或指向外部模板存储的路径）
  - data_sources/           数据源定义与抽象实现
  - migrations/             数据库迁移脚本（若用 Alembic，放此处）
  - tests/                  专门的后端测试用例（入口见 tests/）

- database/                 数据库相关脚本与设计（如 schema、migrations）
- docs/                    与后端相关的文档

## 3. 前端结构（frontend/）
- src/
  - main.js / main.ts        应用入口
  - App.vue                   根组件
  - router/                    路由定义
  - views/                     页面视图
  - components/                可复用 UI组件
  - store/                     Pinia 状态管理
  - services/                  API 调用封装
  - assets/                    静态资源
- tests/                       前端测试用例

## 4. 数据模型与关系（示意性描述）
- Template: 模板定义、版本、所属组织、状态
- DataSource: 数据源定义、类型、连接信息、授权信息
- FieldMapping: 字段映射用途，绑定模板字段与数据源字段
- DocumentHistory: 生成历史记录，版本号、时间戳、输出路径、状态
- 关系示例：Template 1 --< FieldMapping >--  DataSource 1 以及 DocumentHistory 的关联记录

## 5. 代码风格与约定
- Python/Backend：遵循 PEP 8；使用类型提示，遵循统一的命名约定。
- Frontend：遵循 Vue 3 格式，组件命名与目录结构尽量按功能聚簇。
- 测试：单元测试覆盖核心域模型、服务方法和 API，集成测试覆盖主要工作流。

## 6. 变更与迁移注意事项
- 数据模型的重大改动需逐步迁移，保留兼容层以确保现有数据的可用性。
- 变更应伴随测试用例与迁移脚本，确保回滚可行。
