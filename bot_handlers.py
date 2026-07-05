import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from knowledge_loader import KnowledgeBase
from memory import ChatMemory
from openai_client import OpenAIClient

NO_INFORMATION_MESSAGE = "В доступных материалах нет информации по этому вопросу."


def create_router(
    knowledge_base: KnowledgeBase,
    openai_client: OpenAIClient,
    memory: ChatMemory,
    max_context_chars: int,
) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        await _answer(
            message,
            "Здравствуйте. Я личный AI-ассистент кандидата Business Analyst. "
            "Могу кратко ответить на вопросы об опыте, навыках, проектах, кейсах и ссылках портфолио.",
        )

    @router.message(Command("help"))
    async def help_command(message: Message) -> None:
        await _answer(
            message,
            "\n".join(
                [
                    "Примеры вопросов:",
                    "- Какой опыт у кандидата в бизнес-анализе?",
                    "- Какие проекты есть в портфолио?",
                    "- Какие ключевые навыки релевантны для BA-роли?",
                    "- Есть ли кейсы с требованиями, метриками или процессами?",
                    "- Где посмотреть резюме, GitHub или LinkedIn?",
                    "",
                    "Команды: /projects, /skills, /links",
                ]
            ),
        )

    @router.message(Command("projects"))
    async def projects(message: Message) -> None:
        await _answer(message, knowledge_base.get_document_text("projects.md"))

    @router.message(Command("skills"))
    async def skills(message: Message) -> None:
        await _answer(message, knowledge_base.get_document_text("skills.md"))

    @router.message(Command("links"))
    async def links(message: Message) -> None:
        await _answer(message, knowledge_base.get_document_text("links.md"))

    @router.message(F.text)
    async def answer_question(message: Message) -> None:
        question = (message.text or "").strip()
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else None

        logging.info("Incoming question chat_id=%s user_id=%s text=%r", chat_id, user_id, question)

        matches = knowledge_base.search(question)
        if not matches:
            memory.add_user_message(chat_id, question)
            await _answer(message, NO_INFORMATION_MESSAGE)
            return

        context = knowledge_base.build_context(matches, max_chars=max_context_chars)
        recent_messages = memory.get_user_messages(chat_id)

        try:
            answer = await openai_client.generate_answer(
                question=question,
                context=context,
                recent_user_messages=recent_messages,
            )
        except Exception:
            logging.exception("Failed to answer question chat_id=%s", chat_id)
            await _answer(
                message,
                "Не удалось сформировать ответ из-за технической ошибки. Попробуйте позже.",
            )
            return

        memory.add_user_message(chat_id, question)
        await _answer(message, answer or NO_INFORMATION_MESSAGE)

    return router


async def _answer(message: Message, text: str) -> None:
    for chunk in _chunks(text.strip(), limit=3900):
        await message.answer(chunk)


def _chunks(text: str, limit: int) -> list[str]:
    if len(text) <= limit:
        return [text]

    chunks = []
    current = []
    current_len = 0
    for line in text.splitlines():
        line_len = len(line) + 1
        if current and current_len + line_len > limit:
            chunks.append("\n".join(current))
            current = []
            current_len = 0
        current.append(line)
        current_len += line_len

    if current:
        chunks.append("\n".join(current))

    return chunks
