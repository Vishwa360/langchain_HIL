"""
FastAPI test harness for the HITL stock-research agent.

Send a message payload shaped like:
{
    "role": "user",
    "content": "Yahoo Finance",
    "thread_id": "optional-thread-id",
    "auto_approve": true
}
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from langgraph.types import Command

from main import build_agent

app = FastAPI(title="HITL Stock Research API")

# Build the agent once at startup
agent = build_agent()


class ChatRequest(BaseModel):
    role: str = Field(default="user")
    content: str
    thread_id: str | None = None
    auto_approve: bool = True


@app.post("/chat")
async def chat(req: ChatRequest):
    """
    Single-turn HITL call. If an interrupt is returned, auto-approve by default.
    """
    config = {"configurable": {"thread_id": req.thread_id or "api-thread"}}
    messages = [{"role": req.role, "content": req.content}]

    try:
        result = agent.invoke({"messages": messages}, config=config)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    hop = 0
    events = [{"stage": "initial", "result": result}]

    # Auto-resume any interrupt so calls don't hang.
    while "__interrupt__" in result and req.auto_approve and hop < 3:
        resume = {"decisions": [{"type": "approve"}]}
        try:
            result = agent.invoke(Command(resume=resume), config=config)
        except Exception as exc:  # noqa: BLE001
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        hop += 1
        events.append({"stage": f"resume_{hop}", "result": result})

    return {
        "final": result['messages'][-1].content,
        "stages": events,
        "auto_approve": req.auto_approve,
    }


@app.get("/health")
async def health():
    # Lightweight readiness signal; no external calls.
    tool_names = [t.name for t in getattr(agent, "tools", [])] if hasattr(agent, "tools") else []
    return {
        "status": "ok",
        "tools": tool_names,
        "auto_approve_default": True,
    }
