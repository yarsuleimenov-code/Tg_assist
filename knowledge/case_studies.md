# Кейсы

## Кейс 1. SmartQuote / Zaberman Broker Calculator

Бизнес-вопрос:
Как ускорить и стандартизировать расчет quote для interstate-перевозок, сохранив прозрачность pricing logic для broker/admin/CEO review?

Пользователь:
Sales broker / admin user, который должен быстро создать quote, проверить расчет, сгенерировать customer-facing estimate и сохранить snapshot.

Подход:
- описан broker-first workflow: route -> items -> access conditions -> quote options -> pricing result -> generate estimate;
- выделены слои: commercial pricing layer и operational execution layer;
- определены ключевые сущности: QuoteDraft, QuoteItem, PricingVariables, PricingBreakdown, Estimate, EstimateSnapshot, Invoice, Order, eBOL;
- описана логика immutable estimate snapshots;
- подготовлены pricing test cases, operational edge cases, developer handoff и technical roadmap;
- Cost Breakdown v2 сделан как CFO/CEO review surface с reconciliation и Formula Trace.

Результат:
- working test-mode MVP / visual technical specification;
- Quick Quote / Full Quote -> Estimate Document flow;
- зафиксирована roadmap для production pricing engine;
- снижена неопределенность между бизнесом, CEO и разработкой.

Ограничения:
это не production-ready backend. Production scope требует database, pricing service, validation, audit trail, PDF/export, auth и controlled variable governance.

## Кейс 2. Warehouse Control Platform / Loading Control v2

Бизнес-вопрос:
Как сделать загрузку и приемку груза проверяемой, если текущая система хранит только агрегированный счетчик LoadedPieces?

Пользователь:
Warehouse user в NY/CA loading и unloading workflow.

Проблема текущей версии:
- система знает только `loaded / total`, но не знает, какие конкретно pieces загружены;
- spreadsheet row number используется как fragile identifier;
- нет durable trip/report snapshot;
- нет timestamps по конкретным piece actions;
- UI table-first и неудобен для mobile warehouse scenario.

Решение:
- перейти от `Order -> LoadedPieces number` к `Order -> Piece 1..N -> Loaded / LoadedAt / UpdatedAt`;
- ввести sheets `Orders`, `OrderPieces`, `TripReports`;
- сделать единое status rule: Requires Pieces, Not Started, Started, Completed;
- добавить Generate Trip как append-only snapshot;
- сохранить Google Apps Script + Google Sheets как простую MVP-платформу без внешней database.

Результат:
- описана v2 architecture;
- подготовлена warehouse-control-platform с login, workflow selection, truck selection, loading dashboard, unloading MVP и TripReports;
- зафиксированы performance rules: batch reads/writes, stable keys, compact payload, piece details on demand.

## Кейс 3. Client Order Tracking MVP

Бизнес-вопрос:
Как дать клиенту информацию о статусе заказа, не раскрывая внутренние CRM-данные?

Пользователь:
Клиент, который знает свой Order ID и хочет проверить pickup/delivery status.

Решение:
- frontend принимает Order ID;
- Apps Script API читает sheet `public_order_tracking`;
- CRM status мапится в client-facing status;
- frontend показывает статус, pickup/delivery dates, time windows, last update и progress timeline;
- приватные поля не возвращаются в public response.

Результат:
- минимальный public tracking portal;
- data contract с разрешенными и запрещенными полями;
- снижена зависимость клиента от ручных запросов к менеджеру;
- сохранена privacy boundary: не раскрываются полный телефон, адрес, внутренние notes, CRM links, manager, team, package count, weight и spreadsheet URL.

## Кейс 4. Family Menu

Бизнес-вопрос:
Как семье быстро планировать ужины и покупки без сложной backend-архитектуры?

Пользователь:
Семья, которая выбирает ужины, формирует shopping list и отмечает покупки в магазине.

Решение:
- React/Vite frontend с экранами Plan, Shopping, Dishes, Base Products;
- Google Sheets + Apps Script API вместо Supabase/Firebase для v1, потому что важнее простота редактирования и бесплатный запуск;
- mock/localStorage mode для разработки;
- Google Sheets v2 schema для dishes, dish_ingredients, calendar_plan, base_products, shopping_sessions, selected_dinners, settings;
- mobile-first QA и live API smoke tests.

Результат:
- рабочий GitHub Pages app;
- основной сценарий Plan -> dinner selection -> Shopping -> store marks работает;
- dataset: 45 dishes, 44 active; 48 active base products with prices;
- зафиксированы ограничения: Apps Script cold start, отсутствие сложной multi-user синхронизации, approximate prices.

## Кейс 5. AI Portfolio Assistant

Бизнес-вопрос:
Как быстро показать HR релевантный опыт кандидата и дать ответы на типовые вопросы по портфолио?

Пользователь:
HR, recruiter или technical interviewer.

Решение:
- Telegram-бот принимает вопрос;
- локальный keyword search ищет релевантные Markdown-файлы;
- DeepSeek API формирует краткий деловой ответ только на основании knowledge base;
- если данных нет, бот честно отвечает, что информации нет;
- команды `/projects`, `/skills`, `/links` закрывают быстрые сценарии.

Результат:
- рабочий Telegram bot;
- Docker-ready проект;
- GitHub repository;
- Google Cloud VM deployment;
- knowledge base на основе реальных проектов.

Ограничения:
поиск в MVP keyword-based. Для более сложных вопросов можно добавить embeddings/vector search позже, если появится бизнес-необходимость.

## Кейс 6. IITU OLAP Course

Бизнес-вопрос:
Как структурировать образовательный курс по OLAP и integrated planning для студентов/слушателей?

Решение:
- курс разбит на 10 лекций: introduction, architecture, IBP, S&OP, logistics, budgeting, financial analysis, KPI, security, future;
- подготовлены web pages и PDF materials;
- создана RU/EN структура.

Результат:
публичный GitHub Pages курс, который демонстрирует способность кандидата структурировать сложную аналитическую тему и превращать ее в понятные учебные материалы.
