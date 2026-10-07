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


API_KEY = "dev-key-123"


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
    @app.get("/tickets")
    def tickets(
    x_api_key: str = Header(default=""),
):
     verify_api_key(x_api_key)

    return {
        "ok": True,
        "tickets": list_tickets(),
    }

    if not result["ok"]:
        raise HTTPException(
            status_code=400,
            detail=result,
        )

    return result


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