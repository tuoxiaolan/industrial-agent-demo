import json

from agent_loop import fake_llm_decide
from tool_dispatcher import execute_tool


WRITE_TOOLS = {
    "create_maintenance_ticket",
}


def need_confirmation(tool_call):
    return tool_call["name"] in WRITE_TOOLS


def show_result(result):
    print(json.dumps(result, ensure_ascii=False, indent=2))


def main():
    print("设备维护Agent实验")
    print("输入 exit、quit 或 退出 可以结束程序")
    print("-" * 50)

    while True:
        question = input("你说：").strip()

        if question.lower() in {"exit", "quit"} or question == "退出":
            print("程序结束")
            break

        if not question:
            continue

        decision = fake_llm_decide(question)

        if not decision["ok"]:
            show_result(decision)
            continue

        tool_call = decision["tool_call"]

        print("Agent准备调用：")
        show_result(tool_call)

        if need_confirmation(tool_call):
            answer = input("这是写入操作，是否确认？输入 y 或 n：").strip().lower()

            if answer != "y":
                print("操作已取消，没有创建工单")
                continue

        result = execute_tool(tool_call)
        print("工具执行结果：")
        show_result(result)
        print("-" * 50)


if __name__ == "__main__":
    main()