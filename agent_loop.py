from tool_dispatcher import execute_tool


FIELD_KEYWORDS = [
    ("提升电机功率", "提升电机功率"),
    ("整粒电机功率", "整粒电机功率"),
    ("处理能力", "整粒生产能力"),
    ("产能", "整粒生产能力"),
    ("生产能力", "整粒生产能力"),
    ("每小时处理", "整粒生产能力"),
    ("净负载", "净负载（含料斗）"),
    ("设备重量", "设备重量"),
    ("重量", "设备重量"),
    ("维护", "年度维护周期"),
    ]
DOCUMENT_KEYWORDS = [
    "sop",
    "流程",
    "操作",
    "故障",
    "排查",
    "如何处理",
    "怎么处理",
    "怎么维护",
    "如何维护",
    "说明书",
    "手册",
]



def find_model(question):
    text = question.upper()

    if "DEVICE-A" in text:
        return "Device-A"

    if "DEVICE-B" in text:
        return "Device-B"

    return None


def find_field(question):
    for keyword, field in FIELD_KEYWORDS:
        if keyword in question:
            return field
        

    return None
def needs_manual_search(question):
    text = question.lower()

    for keyword in DOCUMENT_KEYWORDS:
        if keyword.lower() in text:
            return True

    return False


def find_doc_type(question):
    text = question.lower()

    if any(
        keyword in text
        for keyword in ["维护", "故障", "sop", "检修", "排查"]
    ):
        return "maintenance"

    if any(
        keyword in text
        for keyword in ["说明", "手册", "参数", "功率", "重量", "负载", "电压", "温度"]
    ):
        return "manual"

    return None


def fake_llm_decide(question):
    model = find_model(question)

    if model is None:
        return {
            "ok": False,
            "error": "没有识别到设备型号",
        }

    if "工单" in question or "报修" in question:
        return {
            "ok": True,
            "tool_call": {
                "name": "create_maintenance_ticket",
                "arguments": {
                    "model": model,
                    "issue": question,
                    "evidence": "由agent_loop识别后创建",
                },
            },
        }

    if needs_manual_search(question):
        doc_type = find_doc_type(question)

        arguments = {
            "query": question,
            "model": model,
        }

        if doc_type:
            arguments["doc_type"] = doc_type

        return {
            "ok": True,
            "tool_call": {
                "name": "search_manual",
                "arguments": arguments,
            },
        }

    field = find_field(question)

    if field is None:
        return {
            "ok": False,
            "error": "没有识别到需要查询的参数",
        }

    return {
        "ok": True,
        "tool_call": {
            "name": "get_equipment_parameter",
            "arguments": {
                "model": model,
                "field": field,
            },
        },
    }

    field = find_field(question)

    if field is None:
        return {
            "ok": False,
            "error": "没有识别到需要查询的参数",
        }

    return {
        "ok": True,
        "tool_call": {
            "name": "get_equipment_parameter",
            "arguments": {
                "model": model,
                "field": field,
            },
        },
    }


def run_agent(question):
    decision = fake_llm_decide(question)

    if not decision["ok"]:
        return decision

    tool_call = decision["tool_call"]
    result = execute_tool(tool_call)

    return {
        "ok": result.get("ok", False),
        "tool_call": tool_call,
        "result": result,
    }


if __name__ == "__main__":
    questions = [
        "Device-B的提升电机功率是多少？",
        "Device-A的设备重量是多少？",
        "Device-B的处理能力是多少？",
        "给Device-B创建一个提升电机功率异常工单",
        "它有多重？",
        "Device-B的维护流程是什么？",
        "Device-A的故障排查步骤是什么？",
    ]

    for question in questions:
        print("问题：", question)
        print("结果：", run_agent(question))
        print("-" * 50)