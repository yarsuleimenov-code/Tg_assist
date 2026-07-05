import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot_handlers import create_router
from config import load_settings
from knowledge_loader import KnowledgeBase
from memory import ChatMemory
from openai_client import OpenAIClient


async def main() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )

    settings = load_settings()

    knowledge_base = KnowledgeBase()
    knowledge_base.load()
    if not knowledge_base.documents:
        raise RuntimeError("Knowledge base is empty. Add Markdown files to the knowledge directory.")

    openai_client = OpenAIClient(
        api_key=settings.openai_api_key,
        api_base=settings.deepseek_api_base,
        model=settings.deepseek_model,
    )
    memory = ChatMemory()

    bot = Bot(token=settings.telegram_bot_token)
    dispatcher = Dispatcher()
    dispatcher.include_router(
        create_router(
            knowledge_base=knowledge_base,
            openai_client=openai_client,
            memory=memory,
            max_context_chars=settings.max_context_chars,
        )
    )

    logging.info("Business Analyst portfolio assistant started")
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
