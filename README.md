# 工业设备维护RAG+Agent Demo

## 项目简介

本项目是一个使用模拟设备数据构建的工业设备维护RAG+Agent服务，用于学习设备参数查询、说明书/SOP检索、工具调用和工单创建。

所有设备名称、参数和文档均为虚构数据。

## 核心功能

- 设备参数查询
- 参数同义词映射
- Markdown文档解析和分段
- 关键词检索和元数据过滤
- RAG文档检索
- Agent工具选择
- 模拟工单创建
- 写入操作人工确认
- HTTP API
- API Key认证

## 技术栈

- Python 3.12
- HTTP Server
- Markdown
- JSON
- unittest

## 已支持的模拟设备

- Device-A
- Device-B

## 项目结构

```text
industrial-agent-demo/
├── demo_docs/
├── equipment_tools.py
├── knowledge_tools.py
├── rag_ingest.py
├── rag_search.py
├── tool_dispatcher.py
├── tool_schemas.py
├── agent_loop.py
├── agent_chat.py
├── server.py
├── openapi.json
└── test_*.py