import json
import logging
import time
import uuid

from fastapi import Request
from database import list_tickets
from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from agent_loop import fake_llm_decide
from equipment_tools import (
    create_maintenance_ticket,
    get_equipment_parameter,
)
from tool_dispatcher import execute_tool


app = FastAPI(
    title="工业设备维护Agent服务",
    version="1.0.0",
    description="设备参数查询、RAG检索和工单创建接口",
)
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)

logger = logging.getLogger("industrial_agent")


from config import API_KEY


class TicketRequest(BaseModel):
    model: str
    issue: str
    evidence: str = ""


class ChatRequest(BaseModel):
    question: str


def verify_api_key(x_api_key: str):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Unauthorized",
        )

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = uuid.uuid4().hex
    start_time = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = round(
            (time.perf_counter() - start_time) * 1000,
            2,
        )

        logger.exception(json.dumps({
            "request_id": request_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": 500,
            "duration_ms": duration_ms,
            "error": "unhandled_exception",
        }, ensure_ascii=False))

        raise

    duration_ms = round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )

    response.headers["X-Request-ID"] = request_id

    logger.info(json.dumps({
        "request_id": request_id,
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "duration_ms": duration_ms,
    }, ensure_ascii=False))

    return response

@app.get("/health")
def health():
    return {
        "ok": True,
        "service": "industrial-agent-demo",
        "version": "1.0.0",
    }


@app.get("/parameter")
def parameter(
    model: str,
    field: str,
    x_api_key: str = Header(default=""),
):
    verify_api_key(x_api_key)

    result = get_equipment_parameter(model, field)

    if not result["ok"]:
        raise HTTPException(
            status_code=404,
            detail=result,
        )

    return result


@app.post("/ticket")
def create_ticket(
    request: TicketRequest,
    x_api_key: str = Header(default=""),
):
    verify_api_key(x_api_key)

    result = create_maintenance_ticket(
        model=request.model,
        issue=request.issue,
        evidence=request.evidence,
    )

    if not result["ok"]:
        raise HTTPException(
            status_code=400,
            detail=result,
        )

    return result


@app.get("/tickets")
def tickets(
    x_api_key: str = Header(default=""),
):
    verify_api_key(x_api_key)

    return {
        "ok": True,
        "tickets": list_tickets(),
    }


@app.post("/chat")
def chat(
    request: ChatRequest,
    x_api_key: str = Header(default=""),
):
    verify_api_key(x_api_key)

    question = request.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="问题不能为空",
        )

    decision = fake_llm_decide(question)

    if not decision["ok"]:
        raise HTTPException(
            status_code=400,
            detail=decision,
        )

    tool_call = decision["tool_call"]

    if tool_call["name"] == "create_maintenance_ticket":
        return JSONResponse(
            status_code=202,
            content={
                "ok": False,
                "requires_confirmation": True,
                "tool_call": tool_call,
            },
        )

    result = execute_tool(tool_call)

    if not result.get("ok"):
        raise HTTPException(
            status_code=400,
            detail=result,
        )

    return {
        "ok": True,
        "tool_call": tool_call,
        "result": result,
    }
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8001,
    )