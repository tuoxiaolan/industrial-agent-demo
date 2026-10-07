import json
import threading
import time
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

from server import ParameterHandler


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 8000), ParameterHandler)

    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    time.sleep(0.3)

    try:
        headers = {
            "Content-Type": "application/json",
            "X-API-Key": "dev-key-123",
        }

        payload = {
            "model": "Device-B",
            "issue": "提升电机功率异常",
            "evidence": "说明书应为4.0 kW",
        }

        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")

        request = Request(
            "http://127.0.0.1:8000/ticket",
            data=body,
            headers=headers,
            method="POST",
        )

        with urlopen(request, timeout=5) as response:
            print("状态码：", response.status)
            print(response.read().decode("utf-8"))

    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()