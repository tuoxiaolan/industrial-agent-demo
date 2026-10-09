# 工业设备维护 RAG + Agent Demo

一个面向工业设备维护场景的 RAG + Agent 后端服务 Demo，支持设备参数查询、设备说明书和维护 SOP 检索、模拟工单创建以及写入操作人工确认。

> 本项目全部使用虚构设备和模拟数据，不包含任何公司内部资料。

## 核心功能

- 查询设备结构化参数
- 支持参数同义词转换
- 解析 Markdown 说明书和维护文档
- 按章节拆分文档并保留元数据
- 基于关键词和章节权重进行 RAG 检索
- 使用元数据过滤设备型号和文档类型
- Agent 自动选择参数查询、文档检索或工单工具
- 写入操作增加人工确认机制
- 使用 SQLite 持久化工单
- 提供 FastAPI HTTP 接口
- 支持 API Key 认证和环境变量配置
- 包含请求日志、单元测试、集成测试与评测集

## 技术栈

- Python 3.12
- FastAPI
- Uvicorn
- Pydantic
- python-dotenv
- SQLite
- Markdown
- unittest
- Docker

当前 RAG 检索使用关键词、中文二元组和章节标题加权，尚未接入 Embedding 和向量数据库。Agent 当前使用规则决策模拟 LLM Function Calling，后续可替换为真实模型调用。

## 项目架构

```text
用户
  |
  v
FastAPI / Agent CLI
  |
  v
Agent 决策层
  |-- 参数问题 -> get_equipment_parameter
  |-- 文档问题 -> search_manual
  |-- 工单问题 -> create_maintenance_ticket
  |
  v
工具分发器
  |
  v
参数数据 / RAG 检索 / SQLite 工单数据库
```

## RAG 流程

```text
Markdown 文档
  -> 元数据解析
  -> 按章节拆分
  -> 关键词和中文二元组分词
  -> 元数据过滤
  -> 章节标题加权
  -> TopK 检索结果
  -> 返回正文和来源
```

## Agent 工具

### get_equipment_parameter

查询设备结构化参数。

示例：

```text
Device-B
提升电机功率
```

返回：

```json
{
  "ok": true,
  "model": "Device-B",
  "field": "提升电机功率",
  "value": 4.0,
  "unit": "kW",
  "source": "Device-B-manual.md"
}
```

### search_manual

检索设备说明书、SOP 和维护文档。

示例：

```text
Device-B的维护流程是什么？
```

返回：

```json
{
  "ok": true,
  "query": "Device-B的维护流程是什么？",
  "results": [
    {
      "model": "Device-B",
      "doc_type": "maintenance",
      "source": "Device-B-maintenance.md",
      "section": "设备维护流程与故障排查SOP"
    }
  ]
}
```

### create_maintenance_ticket

创建模拟维护工单。

示例：

```json
{
  "model": "Device-B",
  "issue": "提升电机功率异常",
  "evidence": "说明书应为4.0 kW"
}
```

返回：

```json
{
  "ok": true,
  "ticket": {
    "ticket_id": "MT-0001",
    "model": "Device-B",
    "issue": "提升电机功率异常",
    "evidence": "说明书应为4.0 kW",
    "status": "created"
  }
}
```

## 目录结构

```text
industrial-agent-demo/
├── demo_docs/
│   ├── Device-A-manual.md
│   ├── Device-A-maintenance.md
│   ├── Device-B-manual.md
│   └── Device-B-maintenance.md
├── agent_loop.py
├── agent_chat.py
├── config.py
├── database.py
├── equipment_tools.py
├── evaluate_agent.py
├── evaluation_set.json
├── fastapi_app.py
├── knowledge_tools.py
├── rag_ingest.py
├── rag_search.py
├── server.py
├── tool_dispatcher.py
├── tool_schemas.py
├── openapi.json
├── Dockerfile
├── .dockerignore
├── requirements.txt
├── .env.example
├── .gitignore
└── test_*.py
```

## 安装依赖

```powershell
python -m pip install -r requirements.txt
```

如果直接安装：

```powershell
python -m pip install fastapi uvicorn pydantic python-dotenv
```

## 环境变量

创建 `.env`：

```text
EQUIPMENT_API_KEY=dev-key-123
```

`.env.example`：

```text
EQUIPMENT_API_KEY=your-api-key-here
```

`.env`不会上传GitHub。

## 启动服务

```powershell
python -m uvicorn fastapi_app:app --reload --port 8001
```

也可以直接运行 `fastapi_app.py`。

启动后访问接口文档：

```text
http://127.0.0.1:8001/docs
```

健康检查：

```text
http://127.0.0.1:8001/health
```

原来的标准库HTTP服务 `server.py`保留用于教学对比，推荐使用FastAPI版本。

## API 接口

| 方法 | 路径 | 功能 |
| --- | --- | --- |
| GET | /health | 健康检查 |
| GET | /parameter | 查询设备参数 |
| POST | /ticket | 创建维护工单 |
| GET | /tickets | 查询工单列表 |
| POST | /chat | Agent自然语言问答 |

请求头：

```text
x-api-key: dev-key-123
```

## API 示例

### 查询设备参数

```text
GET /parameter?model=Device-B&field=提升电机功率
```

### Agent问答

```json
{
  "question": "Device-B的维护流程是什么？"
}
```

### 创建工单

```json
{
  "model": "Device-B",
  "issue": "提升电机功率异常",
  "evidence": "说明书应为4.0 kW"
}
```

### 查询工单列表

```text
GET /tickets
```

## 数据库

工单保存在项目根目录：

```text
agent.db
```

数据库表：

```text
tickets
- id
- ticket_id
- model
- issue
- evidence
- status
- created_at
```

`agent.db`和`*.db`已加入 `.gitignore`，不会上传GitHub。

## 运行测试

运行Python单元测试：

```powershell
python -m unittest -v
```

运行FastAPI自动测试：

```powershell
python test_fastapi.py
```

运行工单接口集成测试：

```powershell
python test_ticket_selfcontained.py
```

运行Agent聊天接口集成测试：

```powershell
python test_chat_selfcontained.py
```

## Agent决策逻辑

当前使用规则决策模拟大模型的工具选择：

```text
包含“工单”或“报修”
-> create_maintenance_ticket

包含“SOP”“流程”“操作”“故障”“排查”等
-> search_manual

包含明确参数名称
-> get_equipment_parameter

无法识别
-> 返回错误或提示补充信息
```

该决策层可替换为真实LLM Function Calling。

## 日志与安全设计

- API Key通过环境变量读取
- 请求日志记录method、path、status_code、duration_ms和request_id
- 查询类工具可以直接执行
- 写入类工具需要人工确认
- Agent接口不会直接创建工单
- `/chat`对工单请求返回 `requires_confirmation: true`
- 用户确认后再调用 `/ticket`

## Docker部署

已验证以下命令：

```powershell
docker build -t industrial-agent-demo .
```

```powershell
docker run --rm -p 8001:8001 --env-file .env industrial-agent-demo
```

验证结果：

- `/health`：200
- `/parameter`：200
- `/chat`：200
- `/ticket`：200

当前未配置数据库volume，容器删除后 `agent.db`会丢失。

## 验证与评测结果

验证日期：2026-10-08

### 自动化测试

```text
unittest：13/13通过
FastAPI接口测试：通过
工单接口集成测试：通过
Agent聊天接口集成测试：通过
```

### Agent评测集

评测集包含20道测试问题，覆盖参数查询、同义词、维护周期、RAG检索、工单创建、错误型号、无答案问题和跨设备污染。

| 指标 | 结果 | 准确率 |
| --- | ---: | ---: |
| 工具选择 | 20/20 | 100% |
| 参数回答 | 10/10 | 100% |

评测文件：

- `evaluation_set.json`
- `evaluate_agent.py`

## 当前限制

- 参数保存在Python字典中
- RAG使用基础关键词检索，尚未使用BM25、Embedding和向量数据库
- Agent决策使用规则模拟，尚未接入真实LLM
- SQLite数据未挂载Docker volume
- 尚未部署到云端服务器

## 后续计划

- 使用BM25和Embedding改进检索
- 接入真实LLM Function Calling
- 为SQLite配置Docker volume
- 增加CI自动测试
- 扩展评测数据集和错误分析