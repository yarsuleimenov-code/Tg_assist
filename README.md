# Telegram AI Assistant for Business Analyst Portfolio

MVP личного AI-ассистента для портфолио Business Analyst. Бот отвечает HR и рекрутерам на вопросы о кандидате, опыте, навыках, проектах и ссылках портфолио.

## Цель и MVP

Цель: быстро показать релевантный опыт кандидата через Telegram-бота без ручного пересказа резюме.

Минимальный готовый результат:
- пользователь задает текстовый вопрос в Telegram;
- бот ищет релевантную информацию в локальных Markdown-файлах;
- бот формирует краткий деловой ответ через DeepSeek API;
- если факта нет в knowledge base, бот честно отвечает: `В доступных материалах нет информации по этому вопросу.`

## Бизнес-логика

1. HR задает вопрос о кандидате.
2. Бот ищет совпадения в `knowledge/*.md`.
3. В DeepSeek передается только найденный контекст, системный промпт и последние вопросы пользователя.
4. Модель отвечает только на основании подготовленных материалов.
5. Для быстрых сценариев есть команды `/projects`, `/skills`, `/links`.

## Структура

```text
.
├── main.py
├── config.py
├── bot_handlers.py
├── openai_client.py
├── knowledge_loader.py
├── memory.py
├── prompts.py
├── knowledge/
│   ├── profile.md
│   ├── projects.md
│   ├── skills.md
│   ├── case_studies.md
│   └── links.md
├── Dockerfile
├── requirements.txt
├── .env.example
└── AGENTS.md
```

## Команды бота

- `/start` — краткое описание ассистента.
- `/help` — примеры вопросов.
- `/projects` — список проектов.
- `/skills` — список ключевых навыков.
- `/links` — ссылки на портфолио, GitHub, LinkedIn и резюме.

## Запуск локально

1. Создайте Telegram-бота через BotFather и получите токен.
2. Получите DeepSeek API key.
3. Создайте `.env` на основе `.env.example`.

```bash
cp .env.example .env
pip install -r requirements.txt
python main.py
```

Для Windows PowerShell:

```powershell
Copy-Item .env.example .env
pip install -r requirements.txt
python main.py
```

## Переменные окружения

```env
TELEGRAM_BOT_TOKEN=
OPENAI_API_KEY=
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat
MAX_HISTORY_MESSAGES=6
MAX_CONTEXT_CHARS=6000
```

`OPENAI_API_KEY` используется как имя переменной для DeepSeek API key, потому что DeepSeek предоставляет OpenAI-compatible API.

## Docker

```bash
docker build -t ba-portfolio-assistant .
docker run --env-file .env ba-portfolio-assistant
```

## Knowledge Base

Источник знаний находится в папке `knowledge`:
- `profile.md` — краткий профиль кандидата;
- `projects.md` — проекты;
- `skills.md` — навыки;
- `case_studies.md` — кейсы;
- `links.md` — ссылки.

Текущие файлы содержат demo-материалы. Перед публикацией замените их на реальные факты кандидата.

## Демонстрационный сценарий для HR

1. Открыть Telegram-бота и нажать `/start`.
2. Спросить: `Какие проекты есть в портфолио?`
3. Спросить: `Какие навыки кандидата релевантны для Business Analyst?`
4. Спросить: `Есть ли кейс про MVP?`
5. Ввести `/links`, чтобы получить резюме, GitHub, LinkedIn и портфолио.
6. Задать вопрос вне knowledge base и проверить честный fallback.

## Ограничения MVP

- Поиск релевантности простой keyword-based, без vector database.
- История последних 6 сообщений хранится в памяти процесса и сбрасывается после перезапуска.
- Нет админ-панели для редактирования knowledge base.
- Нет авторизации пользователей.

Эти ограничения осознанно оставлены за рамками MVP, чтобы сохранить простоту, скорость реализации и понятность проекта для HR и технического интервьюера.
