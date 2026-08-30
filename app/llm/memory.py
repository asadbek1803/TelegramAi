from collections import defaultdict


class ChatMemory:
    """In-memory suhbat tarixi. Jarayon qayta ishga tushsa tozalanadi."""

    def __init__(self, max_messages: int = 20) -> None:
        self.max_messages = max_messages
        self._store: dict[str, list[dict[str, str]]] = defaultdict(list)

    def get(self, session_id: str) -> list[dict[str, str]]:
        return list(self._store.get(session_id, []))

    def append(self, session_id: str, role: str, content: str) -> None:
        history = self._store[session_id]
        history.append({"role": role, "content": content})
        overflow = len(history) - self.max_messages
        if overflow > 0:
            del history[:overflow]

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)
