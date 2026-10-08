import json

from agent_loop import run_agent


def load_cases():
    with open("evaluation_set.json", "r", encoding="utf-8") as file:
        return json.load(file)


def get_tool_name(result):
    tool_call = result.get("tool_call")

    if not isinstance(tool_call, dict):
        return None

    return tool_call.get("name")


def get_value(result):
    payload = result.get("result")

    if not isinstance(payload, dict):
        return None

    return payload.get("value")


def evaluate_case(case):
    question = case["question"]
    expected_tool = case.get("expected_tool")

    result = run_agent(question)
    actual_tool = get_tool_name(result)

    if expected_tool is None:
        tool_ok = not result.get("ok", False)
        value_ok = None
    else:
        tool_ok = actual_tool == expected_tool

        if "expected_value" in case:
            expected_value = case["expected_value"]
            actual_value = get_value(result)
            value_ok = actual_value == expected_value
        else:
            value_ok = None

    return {
        "id": case["id"],
        "question": question,
        "expected_tool": expected_tool,
        "actual_tool": actual_tool,
        "tool_ok": tool_ok,
        "expected_value": case.get("expected_value"),
        "actual_value": get_value(result),
        "value_ok": value_ok,
        "result": result,
    }


def main():
    cases = load_cases()
    results = []

    for case in cases:
        result = evaluate_case(case)
        results.append(result)

        print("=" * 70)
        print("编号：", result["id"])
        print("问题：", result["question"])
        print("期望工具：", result["expected_tool"])
        print("实际工具：", result["actual_tool"])
        print("工具正确：", result["tool_ok"])
        print("期望参数：", result["expected_value"])
        print("实际参数：", result["actual_value"])

        if result["value_ok"] is not None:
            print("参数正确：", result["value_ok"])

        print("执行结果：", result["result"])

    tool_passed = sum(
        1 for result in results if result["tool_ok"]
    )

    value_results = [
        result
        for result in results
        if result["value_ok"] is not None
    ]

    value_passed = sum(
        1 for result in value_results if result["value_ok"]
    )

    print()
    print("=" * 70)
    print(
        f"工具选择正确率：{tool_passed}/{len(results)}"
    )

    if value_results:
        print(
            f"参数回答正确率：{value_passed}/{len(value_results)}"
        )


if __name__ == "__main__":
    main()