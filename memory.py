from collections import defaultdict, deque


class ChatMemory:
    def __init__(self, limit: int = 6) -> None:
        self._messages = defaultdict(lambda: deque(maxlen=limit))

    def add_user_message(self, chat_id: int, text: str) -> None:
        self._messages[chat_id].append(text)

    def get_user_messages(self, chat_id: int) -> list[str]:
        return list(self._messages[chat_id])
