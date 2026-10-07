import json


TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "get_equipment_parameter",
            "description": "查询指定设备型号的结构化参数，例如功率、重量、负载和维护周期。",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "设备型号，例如Device-A或Device-B",
                    },
                    "field": {
                        "type": "string",
                        "description": "参数名称，例如提升电机功率、设备重量",
                    },
                },
                "required": ["model", "field"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_maintenance_ticket",
            "description": "为设备问题创建维护工单。",
            "parameters": {
                "type": "object",
                "properties": {
                    "model": {
                        "type": "string",
                        "description": "设备型号",
                    },
                    "issue": {
                        "type": "string",
                        "description": "设备问题描述",
                    },
                    "evidence": {
                        "type": "string",
                        "description": "支持创建工单的依据或原文信息",
                    },
                },
                "required": ["model", "issue"],
            },
        },
    },
        {
        "type": "function",
        "function": {
            "name": "search_manual",
            "description": "检索设备说明书、SOP和维护文档。",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "用户要检索的问题",
                    },
                    "model": {
                        "type": "string",
                        "description": "设备型号，例如Device-A或Device-B",
                    },
                    "doc_type": {
                        "type": "string",
                        "description": "文档类型，例如manual或maintenance",
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "返回结果数量，默认5",
                    },
                },
                "required": ["query"],
            },
        },
    },
]


if __name__ == "__main__":
    print(json.dumps(TOOL_SCHEMAS, ensure_ascii=False, indent=2))