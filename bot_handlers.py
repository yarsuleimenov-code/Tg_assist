import logging
import re

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from intent_router import Intent, IntentResult, is_general_portfolio_question, parse_llm_intent, route_intent
from knowledge_loader import KnowledgeBase
from memory import ChatMemory
from openai_client import OpenAIClient

NO_INFORMATION_MESSAGE = "В доступных материалах нет информации по этому вопросу."
TECHNICAL_ERROR_MESSAGE = "Не удалось сформировать ответ из-за технической ошибки. Попробуйте позже."
MAX_ANSWER_CHARS = 1500
LOG_QUESTION_CHARS = 1000
LOG_ANSWER_CHARS = 2500
MAIN_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Проекты"), KeyboardButton(text="Навыки")],
        [KeyboardButton(text="Ссылки"), KeyboardButton(text="Помощь")],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите команду или задайте вопрос",
)
GREETING_MESSAGE = (
    "Здравствуйте. Я ИИслав, цифровой помощник Ярослава Сулейменова. "
    "Могу ответить на вопросы о его опыте, проектах, навыках и ссылках портфолио. "
    "Также кратко помогаю с профессиональными BA-темами: требования, процессы, KPI, MVP и продуктовая логика."
)
PROJECTS_OVERVIEW = "\n".join(
    [
        "Проекты Ярослава лучше смотреть как портфолио практического Business Analyst / Product Engineer: не просто код, а кейсы, где бизнес-задача доведена до работающего MVP, понятной логики и демонстрации.",
        "",
        "1. SmartQuote / Zaberman Calculator",
        "Pricing-платформа для moving-бизнеса: quote flow, расчет стоимости, estimate lifecycle, cost breakdown и подготовка к production handoff.",
        "Ценность: показывает умение разбирать сложную pricing logic и переводить ее в понятный продуктовый интерфейс.",
        "Демо: https://yarsuleimenov-code.github.io/Zaberman_calc/orders.html",
        "",
        "2. Warehouse Control / Loading Control",
        "Операционный workflow для склада: загрузка, приемка, piece-level tracking, trip reports и контроль статусов.",
        "Ценность: сильный кейс по процессам, данным, ролям пользователей и MVP для внутренних операций.",
        "",
        "3. AI Portfolio Assistant",
        "Telegram-бот ИИслав: отвечает HR по портфолио, работает с локальной knowledge base, Docker и Google Cloud VM.",
        "Ценность: демонстрирует end-to-end подход: требования, архитектура, реализация, деплой и улучшение UX.",
        "",
        "4. Portfolio / Analytics Hub",
        "Публичная витрина проектов, опыта, ссылок и аналитических кейсов.",
        "Демо: https://yarsuleimenov-code.github.io/ys-analytics/",
        "",
        "5. Family Menu и IITU OLAP Course",
        "Дополнительные кейсы по продуктовой логике, планированию, аналитике, BI/OLAP и структурированию знаний.",
        "",
        "Если нужно, могу раскрыть любой проект отдельно: бизнес-задача, роль Ярослава, результат, стек или ссылка на демо.",
    ]
)


def create_router(
    knowledge_base: KnowledgeBase,
    openai_client: OpenAIClient,
    memory: ChatMemory,
    max_context_chars: int,
    log_chat_id: str | None = None,
) -> Router:
    router = Router()

    @router.message(CommandStart())
    async def start(message: Message) -> None:
        await _answer(
            message,
            GREETING_MESSAGE,
            log_chat_id=log_chat_id,
        )

    @router.message(Command("help"))
    async def help_command(message: Message) -> None:
        await _answer(
            message,
            "\n".join(
                [
                    "Примеры вопросов о кандидате:",
                    "- Какие проекты есть в портфолио?",
                    "- Какие навыки кандидата релевантны для BA-роли?",
                    "- Есть ли кейсы по MVP или аналитике?",
                    "- Где посмотреть резюме, GitHub или LinkedIn?",
                    "",
                    "Примеры профессиональных вопросов:",
                    "- Как определить scope MVP?",
                    "- Как описать acceptance criteria?",
                    "- Чем user story отличается от use case?",
                    "- Как выбрать KPI для dashboard?",
                    "",
                    "Команды: /projects, /skills, /links",
                ]
            ),
            log_chat_id=log_chat_id,
        )

    @router.message(Command("projects"))
    async def projects(message: Message) -> None:
        await _answer(message, PROJECTS_OVERVIEW, mode=Intent.PORTFOLIO, log_chat_id=log_chat_id)

    @router.message(Command("skills"))
    async def skills(message: Message) -> None:
        await _answer(message, knowledge_base.get_document_text("skills.md"), log_chat_id=log_chat_id)

    @router.message(Command("links"))
    async def links(message: Message) -> None:
        await _answer(message, knowledge_base.get_document_text("links.md"), log_chat_id=log_chat_id)

    @router.message(F.text)
    async def answer_question(message: Message) -> None:
        question = (message.text or "").strip()
        chat_id = message.chat.id
        user_id = message.from_user.id if message.from_user else None

        if _is_greeting(question):
            logging.info("Incoming greeting chat_id=%s user_id=%s text=%r", chat_id, user_id, question)
            await _answer(message, GREETING_MESSAGE, log_chat_id=log_chat_id)
            return

        fast_answer = _fast_answer_text(question, knowledge_base)
        if fast_answer:
            logging.info("Fast answer chat_id=%s user_id=%s text=%r", chat_id, user_id, question)
            memory.update(chat_id, "fast_answer", _fast_answer_topic(question), question)
            await _answer(message, fast_answer, mode=Intent.PORTFOLIO, log_chat_id=log_chat_id)
            return

        route = route_intent(question)
        llm_router_used = route.needs_llm
        if route.needs_llm:
            route = await _resolve_low_confidence_route(question, route, openai_client, chat_id)

        logging.info(
            "Incoming question chat_id=%s user_id=%s intent=%s confidence=%.2f topic=%s llm_router=%s text=%r",
            chat_id,
            user_id,
            route.intent.value,
            route.confidence,
            route.topic,
            llm_router_used,
            question,
        )

        if route.intent == Intent.PORTFOLIO:
            await _answer_portfolio_question(
                message=message,
                question=question,
                route=route,
                chat_id=chat_id,
                knowledge_base=knowledge_base,
                openai_client=openai_client,
                memory=memory,
                max_context_chars=max_context_chars,
                log_chat_id=log_chat_id,
            )
            return

        if route.intent == Intent.PROFESSIONAL:
            await _answer_professional_question(
                message=message,
                question=question,
                route=route,
                chat_id=chat_id,
                openai_client=openai_client,
                memory=memory,
                log_chat_id=log_chat_id,
            )
            return

        if route.intent == Intent.CLARIFICATION:
            previous_topic = memory.get_state(chat_id).last_topic
            memory.update(chat_id, route.intent.value, route.topic, question)
            await _answer(
                message,
                _clarification_message(previous_topic),
                log_chat_id=log_chat_id,
            )
            return

        memory.update(chat_id, route.intent.value, route.topic, question)
        await _answer(message, _out_of_scope_message(), log_chat_id=log_chat_id)

    return router


async def _resolve_low_confidence_route(
    question: str,
    route: IntentResult,
    openai_client: OpenAIClient,
    chat_id: int,
) -> IntentResult:
    try:
        label = await openai_client.classify_intent(question)
    except Exception:
        logging.exception("Failed to classify intent chat_id=%s", chat_id)
        return route
    return parse_llm_intent(label, fallback=route)


async def _answer_portfolio_question(
    message: Message,
    question: str,
    route: IntentResult,
    chat_id: int,
    knowledge_base: KnowledgeBase,
    openai_client: OpenAIClient,
    memory: ChatMemory,
    max_context_chars: int,
    log_chat_id: str | None,
) -> None:
    matches = knowledge_base.search(question)
    if matches:
        context = knowledge_base.build_context(matches, max_chars=max_context_chars)
    elif is_general_portfolio_question(question):
        context = knowledge_base.build_context_from_files(
            ("profile.md", "projects.md", "skills.md", "links.md"),
            max_chars=max_context_chars,
        )
    else:
        memory.update(chat_id, route.intent.value, route.topic, question)
        await _answer(message, NO_INFORMATION_MESSAGE, log_chat_id=log_chat_id)
        return

    logging.info(
        "Portfolio context chat_id=%s matches=%s context_chars=%s top_sources=%s",
        chat_id,
        len(matches),
        len(context),
        [match.chunk.source_file for match in matches[:3]],
    )

    try:
        answer = await openai_client.generate_answer(
            question=question,
            context=context,
            memory_context=memory.get_prompt_context(chat_id),
        )
    except Exception:
        logging.exception("Failed to answer portfolio question chat_id=%s", chat_id)
        await _answer(message, TECHNICAL_ERROR_MESSAGE, log_chat_id=log_chat_id)
        return

    memory.update(chat_id, route.intent.value, route.topic, question)
    logging.info("Portfolio answer chat_id=%s answer_chars=%s", chat_id, len(answer or ""))
    await _answer(message, answer or NO_INFORMATION_MESSAGE, mode=route.intent, log_chat_id=log_chat_id)


async def _answer_professional_question(
    message: Message,
    question: str,
    route: IntentResult,
    chat_id: int,
    openai_client: OpenAIClient,
    memory: ChatMemory,
    log_chat_id: str | None,
) -> None:
    try:
        answer = await openai_client.generate_professional_answer(
            question=question,
            memory_context=memory.get_prompt_context(chat_id),
        )
    except Exception:
        logging.exception("Failed to answer professional question chat_id=%s", chat_id)
        await _answer(message, TECHNICAL_ERROR_MESSAGE, log_chat_id=log_chat_id)
        return

    memory.update(chat_id, route.intent.value, route.topic, question)
    logging.info("Professional answer chat_id=%s answer_chars=%s", chat_id, len(answer or ""))
    await _answer(message, answer or TECHNICAL_ERROR_MESSAGE, mode=route.intent, log_chat_id=log_chat_id)


async def _answer(
    message: Message,
    text: str,
    mode: Intent | None = None,
    log_chat_id: str | None = None,
) -> None:
    text = _apply_guardrails(text, mode=mode)
    chunks = _chunks(text.strip(), limit=3900)
    for index, chunk in enumerate(chunks):
        await message.answer(chunk, reply_markup=MAIN_KEYBOARD if index == 0 else None)
    await _send_interaction_log(message, text, log_chat_id)


async def _send_interaction_log(message: Message, answer: str, log_chat_id: str | None) -> None:
    if not log_chat_id:
        return

    try:
        await message.bot.send_message(
            chat_id=log_chat_id,
            text=_build_interaction_log(message, answer),
            parse_mode=None,
        )
    except Exception:
        user_id = message.from_user.id if message.from_user else None
        logging.exception(
            "Failed to send interaction log chat_id=%s user_id=%s log_chat_id=%s",
            message.chat.id,
            user_id,
            log_chat_id,
        )


def _build_interaction_log(message: Message, answer: str) -> str:
    user = message.from_user
    user_id = user.id if user else None
    question = _truncate_for_log((message.text or "").strip(), LOG_QUESTION_CHARS)
    answer = _truncate_for_log(answer.strip(), LOG_ANSWER_CHARS)

    if user and user.username:
        user_label = f"@{user.username}"
    elif user and user.first_name:
        user_label = f"{user.first_name} / {user.id}"
    elif user_id:
        user_label = str(user_id)
    else:
        user_label = "unknown"

    return "\n".join(
        [
            "New bot interaction",
            "",
            f"User: {user_label}",
            f"User ID: {user_id or 'unknown'}",
            "",
            "Question:",
            question,
            "",
            "Answer:",
            answer,
        ]
    )


def _truncate_for_log(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text

    suffix = "\n...[truncated]"
    body_limit = max(0, limit - len(suffix))
    return f"{text[:body_limit].rstrip()}{suffix}"


def _is_greeting(text: str) -> bool:
    normalized = " ".join(text.lower().strip().split())
    return normalized in {
        "привет",
        "здравствуйте",
        "добрый день",
        "доброе утро",
        "добрый вечер",
        "hello",
        "hi",
    }


def _fast_answer_text(question: str, knowledge_base: KnowledgeBase) -> str | None:
    normalized = " ".join(question.lower().strip().split())

    if normalized in {
        "что ты умеешь",
        "что умеешь",
        "помощь",
        "/help",
        "команды",
        "help",
        "что можно спросить",
    }:
        return "\n".join(
            [
                GREETING_MESSAGE,
                "",
                "Можно спросить:",
                "- какие проекты есть в портфолио;",
                "- какие навыки релевантны для BA-роли;",
                "- где посмотреть GitHub, LinkedIn или резюме;",
                "- как подойти к MVP, требованиям, KPI или процессам.",
            ]
        )

    if normalized in {"/projects", "покажи проекты", "список проектов", "проекты", "дай проекты"}:
        return PROJECTS_OVERVIEW

    if normalized in {"/skills", "покажи навыки", "список навыков", "навыки", "дай навыки"}:
        return knowledge_base.get_document_text("skills.md")

    if normalized in {
        "/links",
        "покажи ссылки",
        "дай ссылки",
        "ссылки",
        "контакты",
        "github",
        "linkedin",
        "резюме",
    }:
        return knowledge_base.get_document_text("links.md")

    if normalized in {
        "что ты знаешь",
        "кто кандидат",
        "кто такой ярослав",
        "кто такой ярослав сулейменов",
        "расскажи о кандидате",
        "расскажи про кандидата",
        "что знаешь о ярославе",
        "профиль кандидата",
    }:
        return knowledge_base.get_document_text("profile.md")

    return None


def _fast_answer_topic(question: str) -> str:
    normalized = " ".join(question.lower().strip().split())
    if "проект" in normalized:
        return "projects"
    if "навык" in normalized:
        return "skills"
    if any(marker in normalized for marker in ("ссыл", "github", "linkedin", "резюме", "контакт")):
        return "links"
    if "кандидат" in normalized or "ярослав" in normalized:
        return "profile"
    return "capabilities"


def _apply_guardrails(text: str, mode: Intent | None = None) -> str:
    cleaned = _format_telegram_text(text)
    if mode in {Intent.PORTFOLIO, Intent.PROFESSIONAL} and len(cleaned) > MAX_ANSWER_CHARS:
        cleaned = _trim_to_limit(cleaned, MAX_ANSWER_CHARS)
    return cleaned or TECHNICAL_ERROR_MESSAGE


def _format_telegram_text(text: str) -> str:
    lines = []

    for raw_line in text.strip().splitlines():
        line = raw_line.strip()

        if not line:
            lines.append("")
            continue

        if re.fullmatch(r"[-*_]{3,}", line):
            continue

        if _is_markdown_table_separator(line):
            continue

        if _is_markdown_table_row(line):
            cells = [cell.strip() for cell in line.strip("|").split("|")]
            line = " | ".join(cell for cell in cells if cell)

        line = re.sub(r"^#{1,6}\s*", "", line)
        line = re.sub(r"^\s*>\s*", "", line)
        line = re.sub(r"\*\*(.*?)\*\*", r"\1", line)
        line = re.sub(r"__(.*?)__", r"\1", line)
        line = re.sub(r"`([^`]+)`", r"\1", line)
        line = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1: \2", line)

        lines.append(line)

    return _collapse_blank_lines("\n".join(lines))


def _trim_to_limit(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text

    suffix = "\n\nМогу раскрыть подробнее по конкретному пункту."
    body_limit = max(200, limit - len(suffix) - 1)
    trimmed = text[:body_limit].rsplit(".", maxsplit=1)[0].strip()
    if len(trimmed) < body_limit * 0.6:
        trimmed = text[:body_limit].rsplit("\n", maxsplit=1)[0].strip()
    if not trimmed:
        trimmed = text[:body_limit].strip()
    return f"{trimmed}.{suffix}"


def _clarification_message(last_topic: str = "") -> str:
    if last_topic in {"projects", "skills", "links", "profile"}:
        return (
            "Уточните, пожалуйста, что именно раскрыть дальше.\n"
            "1. Нужен краткий ответ по портфолио кандидата или профессиональный BA-комментарий?\n"
            "2. Какой аспект важнее: бизнес-задача, роль кандидата, результат или ссылка?"
        )

    return (
        "Уточните, пожалуйста, контекст.\n"
        "1. Вопрос про кандидата и его портфолио или про профессиональную BA-тему?\n"
        "2. Какой результат нужен: краткое объяснение, пример или рекомендация?"
    )


def _out_of_scope_message() -> str:
    return (
        "Я полезен для вопросов о портфолио кандидата и профессиональных темах Business Analysis, "
        "Product, System Analysis, KPI, требованиях и процессах. По этому вопросу лучше использовать другой источник."
    )


def _is_markdown_table_row(line: str) -> bool:
    return line.startswith("|") and line.endswith("|") and line.count("|") >= 2


def _is_markdown_table_separator(line: str) -> bool:
    if not _is_markdown_table_row(line):
        return False
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    return all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells if cell)


def _collapse_blank_lines(text: str) -> str:
    return re.sub(r"\n{3,}", "\n\n", text).strip()


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
