# Проекты

## AI Portfolio Assistant

Telegram-бот для HR и рекрутеров, который отвечает на вопросы о кандидате на основании локальной Markdown knowledge base.

Бизнес-задача:
дать HR быстрый способ получить структурированные ответы об опыте, навыках, проектах и ссылках кандидата без ручного пересказа резюме.

Роль кандидата:
- определение MVP scope;
- формализация функциональных и нефункциональных требований;
- проектирование knowledge base;
- реализация Python/aiogram/DeepSeek API прототипа;
- подготовка Docker, README, GitHub-ready структуры и деплой на Google Cloud VM.

Результат:
- рабочий Telegram-бот;
- локальная база знаний в Markdown;
- запуск в Docker на VPS;
- демонстрационный HR-сценарий.

Стек:
Python, aiogram, DeepSeek API, python-dotenv, Markdown, Docker, GitHub, Google Cloud VM.

## SmartQuote / Zaberman Broker Calculator

Проект broker-first калькулятора для interstate-перевозок мебели, fragile cargo и full service delivery. Включает quote creation, pricing breakdown, estimate document, drafts, estimates, invoice/order/eBOL lifecycle reference и подготовку production handoff.

Источники:
- `E:\Codex\Calc_project`
- `https://github.com/yarsuleimenov-code/SmartQuote`
- `https://github.com/yarsuleimenov-code/Zaberman_calc`
- Готовая демонстрационная версия: `https://yarsuleimenov-code.github.io/Zaberman_calc/index.html`

Бизнес-задача:
снизить ручные расчеты, стандартизировать pricing logic, ускорить создание quote и сделать расчет объяснимым для broker/admin/CEO review.

Роль кандидата:
- описание broker workflow;
- моделирование pricing engine flow;
- проектирование estimate lifecycle и immutable snapshots;
- описание сущностей QuoteDraft, QuoteItem, PricingVariables, Estimate, EstimateSnapshot, Invoice, Order, eBOL;
- подготовка docs: architecture, entity model, pricing test cases, operational edge cases, developer handoff;
- проверка расчетов через UAT cases и smoke tests.

Результат:
- working test-mode MVP / visual technical specification;
- рабочий flow Quick Quote / Full Quote -> Estimate Document;
- Cost Breakdown v2 с Price Storyline, route-stage details, reconciliation и Formula Trace;
- сформирована дорожная карта production implementation.

Ограничения:
текущий проект является test-mode MVP / visual technical specification. Production version требует backend pricing engine, database, authentication, validation, audit trail, PDF/export и governed pricing variables.

Стек:
HTML, JavaScript, TailwindCSS CDN, localStorage, Cloudflare Pages Functions, Google Apps Script, Google Sheets, Node-based smoke tests.

## Zaberman Operational Pricing Platform

Hi-fi wireframe и business architecture для внутренней платформы Zaberman: pricing engine, operational dashboard, vehicle allocation, packaging logic, eBOL workflow, estimate/invoice generation, cost breakdown и warehouse/storage logic.

Источник:
- `https://github.com/yarsuleimenov-code/Zaberman-MVP`

Бизнес-задача:
спроектировать единую operational platform для логистических перевозок с высокой вариативностью грузов и сложной pricing logic.

Роль кандидата:
- формализация бизнес-целей системы;
- проектирование основных экранов: Dashboard, New Calculation, Items Management, Cost Breakdown, eBOL, Variables;
- описание основных сущностей: Lead, Customer, Estimate, Order, Shipment, Item, Vehicle, Route, Invoice, Payment, eBOL;
- фиксация MVP limitations и roadmap.

Результат:
визуальная и логическая основа для обсуждения будущей production-системы с бизнесом и разработкой.

Стек:
HTML, Tailwind CSS, Chart.js. Backend и интеграции описаны как planned scope.

## Warehouse Control Platform / Loading Control

Google Apps Script Web App для warehouse loading/unloading workflows.

Источники:
- `E:\Codex\Loading_control`
- `https://github.com/yarsuleimenov-code/warehouse-control-platform`

Бизнес-задача:
заменить простой счетчик загруженных мест на понятный mobile-first процесс, где warehouse user видит конкретные pieces, отмечает загрузку/приемку и формирует trip snapshot.

Роль кандидата:
- анализ текущей версии Loading Control v1;
- выявление слабых мест: нет piece-level data, нет audit trail по конкретным местам, row number как нестабильный identifier, desktop-first UI;
- проектирование v2 data model: Orders, OrderPieces, TripReports;
- описание status logic, data flows, performance approach и MVP architecture;
- подготовка loading/unloading workflow с NY/CA branches, truck selection, offline pending queue и Generate Trip.

Результат:
- архитектура v2 с переходом от `LoadedPieces number` к `Order -> Piece 1..N -> Loaded / LoadedAt / UpdatedAt`;
- MVP warehouse platform с login через Users sheet, loading dashboard, unloading MVP и TripReports;
- зафиксированы ограничения: plain-text passwords для MVP speed, advanced unloading statuses и auto closing не реализованы.

Стек:
Google Apps Script, Google Spreadsheet, HTML frontend.

## Client Order Tracking MVP

Клиентский портал отслеживания заказа по Order ID.

Источник:
- `E:\Codex\Client_tracker`

Бизнес-задача:
дать клиенту простой публичный способ проверить статус заказа без раскрытия внутренних CRM-полей.

Основной сценарий:
клиент вводит Order ID, frontend отправляет POST в Apps Script Web App, backend читает Google Spreadsheet sheet `public_order_tracking`, мапит CRM status в client-facing status и возвращает публичный ответ.

Роль кандидата:
- определение MVP flow;
- проектирование data contract;
- ограничение публичных полей;
- описание status mapping и test cases;
- отделение frontend от прямого доступа к Google Spreadsheet.

Результат:
- статический frontend;
- Google Apps Script API;
- Google Spreadsheet как source of truth;
- privacy-by-design: не возвращаются полный телефон, внутренние заметки, CRM links, менеджер, команда, адрес, вес, количество мест и spreadsheet URL.

Стек:
HTML, CSS, JavaScript, Google Apps Script, Google Sheets.

## Family Menu

React Web App для планирования семейных ужинов, списка покупок и базовых продуктов.

Источник:
- `E:\Codex\Family_menu`
- Готовая демонстрационная версия: `https://yarsuleimenov-code.github.io/Family_menu/plan`

Бизнес-задача:
упростить ежедневный семейный сценарий: выбрать ужин, сформировать покупки только по выбранным блюдам, учитывать базовые продукты и сохранять статусы покупок.

Роль кандидата:
- определение MVP scope;
- проектирование основных экранов: Plan, Shopping, Dishes, Base Products;
- выбор простого backend-подхода Google Sheets + Apps Script вместо Supabase/Firebase для v1;
- миграция legacy spreadsheet data в v2 schema;
- QA mobile сценариев и live API smoke tests;
- описание architecture, data quality audit, setup и family test guide.

Результат:
- React/Vite frontend опубликован через GitHub Pages;
- подключены Google Sheets + Apps Script API v2;
- основной сценарий работает: Plan -> выбор ужина -> Shopping -> отметки в магазине;
- dataset: 45 блюд, 44 активных; 48 активных базовых продуктов с ценами;
- mobile QA пройден на ширине 390x844.

Стек:
React, Vite, TypeScript, Google Sheets, Apps Script, GitHub Pages, localStorage/mock mode.

## ys-analytics Portfolio

Личный landing portfolio Business Analyst.

Источник:
- `https://github.com/yarsuleimenov-code/ys-analytics`
- Готовая демонстрационная версия: `https://yarsuleimenov-code.github.io/ys-analytics/`

Бизнес-задача:
собрать в одном месте профиль, кейсы, опыт, сертификаты, CV и ссылки кандидата.

Содержание:
- профиль Business Analyst;
- кейсы и артефакты;
- Broker Calculator System;
- A/B-test push notifications;
- курс по IBP и OLAP;
- automation/reporting и SQL/data checks;
- ссылки на CV, Telegram, LinkedIn и HH resume.

Результат:
портфельный сайт, который показывает переход от B2B sales и операционной аналитики к Business Analysis, internal systems и process automation.

## IITU OLAP Course

Учебный курс по OLAP-системам и интегрированному планированию.

Источник:
- `https://github.com/yarsuleimenov-code/IITU_OLAP_Course`
- Готовая демонстрационная версия: `https://yarsuleimenov-code.github.io/IITU_OLAP_Course/`

Бизнес-задача:
структурировать образовательные материалы по OLAP, IBP, S&OP, логистике, бюджетированию, финансовому анализу, KPI, безопасности и будущему integrated planning.

Роль кандидата:
- подготовка структуры курса;
- создание web-страниц лекций;
- публикация PDF-материалов;
- двуязычная структура RU/EN.

Результат:
публичный GitHub Pages курс с 10 лекциями и материалами в PDF.

## A/B-test Push Notifications

Аналитический кейс из портфолио ys-analytics.

Бизнес-задача:
оценить влияние push-уведомлений на конверсию, средний чек и региональные показатели.

Результат по портфолио:
- средний чек: +11.9%;
- конверсия: +4.3 п.п.;
- подготовлены инфографика и notebook-ссылка.
