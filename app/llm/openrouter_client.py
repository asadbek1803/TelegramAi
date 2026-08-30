from collections.abc import AsyncIterator

from openai import AsyncOpenAI

from app.config import settings
from app.llm.memory import ChatMemory
from app.llm.persona import SYSTEM_PROMPT

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


class LLMService:
    def __init__(self, memory: ChatMemory) -> None:
        self.memory = memory
        self._client: AsyncOpenAI | None = None

    @property
    def client(self) -> AsyncOpenAI:
        if self._client is None:
            if not settings.openrouter_api_key:
                raise RuntimeError(
                    "OPENROUTER_API_KEY topilmadi. .env fayliga kalitni yozing: "
                    "https://openrouter.ai/keys"
                )
            self._client = AsyncOpenAI(
                base_url=OPENROUTER_BASE_URL,
                api_key=settings.openrouter_api_key,
            )
        return self._client

    def _messages(self, session_id: str, user_text: str) -> list[dict[str, str]]:
        history = self.memory.get(session_id)
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": user_text},
        ]

    async def complete(self, session_id: str, user_text: str) -> str:
        messages = self._messages(session_id, user_text)
        response = await self.client.chat.completions.create(
            model=settings.openrouter_model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )
        text = (response.choices[0].message.content or "").strip()
        self.memory.append(session_id, "user", user_text)
        self.memory.append(session_id, "assistant", text)
        return text

    async def stream(self, session_id: str, user_text: str) -> AsyncIterator[str]:
        messages = self._messages(session_id, user_text)
        stream = await self.client.chat.completions.create(
            model=settings.openrouter_model,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True,
        )
        chunks: list[str] = []
        async for event in stream:
            if not event.choices:
                continue
            delta = event.choices[0].delta.content
            if delta:
                chunks.append(delta)
                yield delta
        full = "".join(chunks).strip()
        self.memory.append(session_id, "user", user_text)
        if full:
            self.memory.append(session_id, "assistant", full)
