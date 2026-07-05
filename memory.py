from collections import defaultdict
from dataclasses import dataclass


@dataclass
class ChatState:
    last_mode: str = ""
    last_topic: str = ""
    last_user_question: str = ""

    def as_prompt_context(self) -> str:
        if not any((self.last_mode, self.last_topic, self.last_user_question)):
            return "Контекста предыдущего сообщения нет."

        parts = []
        if self.last_mode:
            parts.append(f"Предыдущий режим: {self.last_mode}")
        if self.last_topic:
            parts.append(f"Предыдущая тема: {self.last_topic}")
        if self.last_user_question:
            parts.append(f"Предыдущий вопрос: {self.last_user_question}")
        return "\n".join(parts)


class ChatMemory:
    def __init__(self) -> None:
        self._states = defaultdict(ChatState)

    def update(self, chat_id: int, mode: str, topic: str, question: str) -> None:
        self._states[chat_id] = ChatState(
            last_mode=mode,
            last_topic=topic,
            last_user_question=question,
        )

    def get_state(self, chat_id: int) -> ChatState:
        return self._states[chat_id]

    def get_prompt_context(self, chat_id: int) -> str:
        return self.get_state(chat_id).as_prompt_context()
