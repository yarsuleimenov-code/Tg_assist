import logging

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from knowledge_loader import KnowledgeBase
from memory import ChatMemory
from openai_client import OpenAIClient

NO_INFORMATION_MESSAGE = "В доступных материалах нет информации по этому вопросу."
TECHNICAL_ERROR_MESSAGE = "Не удалось сформировать ответ из-за технической ошибки. Попробуйте позже."


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
            "Отвечаю на вопросы об опыте, проектах, навыках и ссылках портфолио. "
            "Также могу поддержать профессиональный диалог по бизнес-анализу, требованиям, процессам, KPI и MVP.",
        )

    @router.message(Command("help"))
    async def help_command(message: Message) -> None:
        await _answer(
            message,
            "\n".join(
                [
                    "Примеры вопросов о кандидате:",
                    "- Какой опыт у кандидата в бизнес-анализе?",
                    "- Какие проекты есть в портфолио?",
                    "- Какие навыки кандидата релевантны для BA-роли?",
                    "- Где посмотреть резюме, GitHub или LinkedIn?",
                    "",
                    "Примеры профессиональных вопросов:",
                    "- Как правильно описать acceptance criteria?",
                    "- Как определить scope MVP?",
                    "- Чем user story отличается от use case?",
                    "- Как спроектировать KPI dashboard?",
                    "- Как описать data contract для API?",
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

        if _is_portfolio_question(question):
            await _answer_portfolio_question(
                message=message,
                question=question,
                chat_id=chat_id,
                knowledge_base=knowledge_base,
                openai_client=openai_client,
                memory=memory,
                max_context_chars=max_context_chars,
            )
            return

        await _answer_professional_question(
            message=message,
            question=question,
            chat_id=chat_id,
            openai_client=openai_client,
            memory=memory,
        )

    return router


async def _answer_portfolio_question(
    message: Message,
    question: str,
    chat_id: int,
    knowledge_base: KnowledgeBase,
    openai_client: OpenAIClient,
    memory: ChatMemory,
    max_context_chars: int,
) -> None:
    matches = knowledge_base.search(question)
    if matches:
        context = knowledge_base.build_context(matches, max_chars=max_context_chars)
    elif _is_general_portfolio_question(question):
        context = knowledge_base.build_context_from_files(
            ("profile.md", "projects.md", "skills.md", "links.md"),
            max_chars=max_context_chars,
        )
    else:
        memory.add_user_message(chat_id, question)
        await _answer(message, NO_INFORMATION_MESSAGE)
        return

    recent_messages = memory.get_user_messages(chat_id)

    try:
        answer = await openai_client.generate_answer(
            question=question,
            context=context,
            recent_user_messages=recent_messages,
        )
    except Exception:
        logging.exception("Failed to answer portfolio question chat_id=%s", chat_id)
        await _answer(message, TECHNICAL_ERROR_MESSAGE)
        return

    memory.add_user_message(chat_id, question)
    await _answer(message, answer or NO_INFORMATION_MESSAGE)


async def _answer_professional_question(
    message: Message,
    question: str,
    chat_id: int,
    openai_client: OpenAIClient,
    memory: ChatMemory,
) -> None:
    recent_messages = memory.get_user_messages(chat_id)

    try:
        answer = await openai_client.generate_professional_answer(
            question=question,
            recent_user_messages=recent_messages,
        )
    except Exception:
        logging.exception("Failed to answer professional question chat_id=%s", chat_id)
        await _answer(message, TECHNICAL_ERROR_MESSAGE)
        return

    memory.add_user_message(chat_id, question)
    await _answer(message, answer or TECHNICAL_ERROR_MESSAGE)


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


def _is_portfolio_question(text: str) -> bool:
    normalized = text.lower().strip()
    markers = (
        "кандидат",
        "ярослав",
        "сулейменов",
        "портфолио",
        "проект",
        "проекты",
        "кейс",
        "кейсы",
        "опыт",
        "резюме",
        "github",
        "linkedin",
        "hh",
        "ссылк",
        "контакт",
        "навыки кандидата",
        "где работал",
        "smartquote",
        "zaberman",
        "warehouse",
        "loading control",
        "client tracker",
        "family menu",
        "ys-analytics",
        "olap course",
        "iitu",
    )
    return _is_general_portfolio_question(normalized) or any(marker in normalized for marker in markers)


def _is_general_portfolio_question(text: str) -> bool:
    normalized = text.lower().strip()
    markers = (
        "что ты знаешь",
        "расскажи о себе",
        "расскажи о кандидате",
        "расскажи про кандидата",
        "расскажи о ярославе",
        "расскажи про ярослава",
        "кто такой",
        "кто кандидат",
        "о кандидате",
        "о ярославе",
        "чем полезен кандидат",
        "что умеет кандидат",
        "почему его стоит",
        "почему стоит рассмотреть",
        "кратко о кандидате",
        "профиль кандидата",
    )
    return any(marker in normalized for marker in markers)
