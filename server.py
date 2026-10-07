import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from agent_loop import fake_llm_decide
from equipment_tools import (
    create_maintenance_ticket,
    get_equipment_parameter,
)
from tool_dispatcher import execute_tool


API_KEY = "dev-key-123"


class ParameterHandler(BaseHTTPRequestHandler):

    def is_authorized(self):
        request_key = self.headers.get("X-API-Key", "")

        if request_key != API_KEY:
            self.send_json(401, {
                "ok": False,
                "error": "Unauthorized"
            })
            return False

        return True

    def do_GET(self):
        if not self.is_authorized():
            return

        parsed = urlparse(self.path)

        if parsed.path != "/parameter":
            self.send_json(404, {
                "ok": False,
                "error": "Not found"
            })
            return

        query = parse_qs(parsed.query)
        model = query.get("model", [""])[0]
        field = query.get("field", [""])[0]

        result = get_equipment_parameter(model, field)
        self.send_json(200 if result["ok"] else 404, result)

    def do_POST(self):
        if not self.is_authorized():
            return

        parsed = urlparse(self.path)

        if parsed.path not in {"/ticket", "/chat"}:
            self.send_json(404, {
                "ok": False,
                "error": "Not found"
            })
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)

            if parsed.path == "/chat":
                question = data.get("question", "").strip()

                if not question:
                    self.send_json(400, {
                        "ok": False,
                        "error": "问题不能为空"
                    })
                    return

                decision = fake_llm_decide(question)

                if not decision["ok"]:
                    self.send_json(400, decision)
                    return

                tool_call = decision["tool_call"]

                if tool_call["name"] == "create_maintenance_ticket":
                    self.send_json(202, {
                        "ok": False,
                        "requires_confirmation": True,
                        "tool_call": tool_call,
                    })
                    return

                result = execute_tool(tool_call)

                self.send_json(200 if result.get("ok") else 400, {
                    "ok": result.get("ok", False),
                    "tool_call": tool_call,
                    "result": result,
                })
                return

            result = create_maintenance_ticket(
                model=data.get("model", ""),
                issue=data.get("issue", ""),
                evidence=data.get("evidence", ""),
            )

            self.send_json(200 if result["ok"] else 400, result)

        except (ValueError, json.JSONDecodeError) as error:
            self.send_json(400, {
                "ok": False,
                "error": f"请求数据错误：{error}"
            })

    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ParameterHandler)
    print("API已启动：http://127.0.0.1:8000")
    print("参数查询：GET /parameter")
    print("Agent问答：POST /chat")
    print("创建工单：POST /ticket")
    server.serve_forever()