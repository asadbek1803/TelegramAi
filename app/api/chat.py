import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.llm.openrouter_client import LLMService
from app.llm.memory import ChatMemory

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api")


class ChatIn(BaseModel):
    session_id: str = Field(min_length=8, max_length=80)
    message: str = Field(min_length=1, max_length=8000)


class SessionIn(BaseModel):
    session_id: str = Field(min_length=8, max_length=80)


def _sse(payload: dict | str) -> str:
    if isinstance(payload, str):
        return f"data: {payload}\n\n"
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/chat")
async def chat(body: ChatIn, request: Request) -> StreamingResponse:
    llm: LLMService = request.app.state.llm

    async def events() -> AsyncIterator[str]:
        try:
            async for token in llm.stream(body.session_id, body.message.strip()):
                yield _sse({"delta": token})
            yield _sse("[DONE]")
        except RuntimeError as exc:
            yield _sse({"error": str(exc)})
            yield _sse("[DONE]")
        except Exception:
            logger.exception("OpenRouter stream xatosi")
            yield _sse(
                {
                    "error": "Model javob bera olmadi. OPENROUTER_API_KEY va internetni tekshiring."
                }
            )
            yield _sse("[DONE]")

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/chat/new")
async def new_chat(body: SessionIn, request: Request) -> dict:
    memory: ChatMemory = request.app.state.memory
    memory.clear(body.session_id)
    return {"ok": True}
