import json
import threading
import time
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

from server import ParameterHandler


def post_chat(question):
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": "dev-key-123",
    }

    payload = {
        "question": question,
    }

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    request = Request(
        "http://127.0.0.1:8000/chat",
        data=body,
        headers=headers,
        method="POST",
    )

    with urlopen(request, timeout=5) as response:
        print("问题：", question)
        print("状态码：", response.status)
        print(response.read().decode("utf-8"))
        print("-" * 60)


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ParameterHandler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    time.sleep(0.3)

    try:
        post_chat("Device-B的维护流程是什么？")
        post_chat("Device-B的提升电机功率是多少？")
        post_chat("给Device-B创建一个提升电机功率异常工单")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()