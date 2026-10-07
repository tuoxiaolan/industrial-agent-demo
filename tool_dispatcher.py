from knowledge_tools import search_manual
from equipment_tools import (
    create_maintenance_ticket,
    get_equipment_parameter,
)


TOOLS = {
    "get_equipment_parameter": get_equipment_parameter,
    "create_maintenance_ticket": create_maintenance_ticket,
    "search_manual": search_manual,
}


def execute_tool(tool_call):
    name = tool_call.get("name")
    arguments = tool_call.get("arguments", {})

    if name not in TOOLS:
        return {
            "ok": False,
            "error": f"未知工具：{name}",
        }

    try:
        function = TOOLS[name]
        return function(**arguments)
    except TypeError as error:
        return {
            "ok": False,
            "error": f"参数错误：{error}",
        }


if __name__ == "__main__":
    calls = [
        {
            "name": "get_equipment_parameter",
            "arguments": {
                "model": "Device-B",
                "field": "提升电机功率",
            },
        },
        {
            "name": "get_equipment_parameter",
            "arguments": {
                "model": "Device-B",
                "field": "处理能力",
            },
        },
        {
            "name": "create_maintenance_ticket",
            "arguments": {
                "model": "Device-B",
                "issue": "提升电机功率异常",
                "evidence": "应为4.0 kW",
            },
        },
                {
            "name": "search_manual",
            "arguments": {
                "query": "Device-B处理能力",
                "model": "Device-B",
                "doc_type": "manual",
            },
        },
    ]

    for call in calls:
        print("工具调用：", call)
        print("执行结果：", execute_tool(call))
        print("-" * 40)