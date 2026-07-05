# Project Instructions

## Goal

MVP Telegram AI assistant for a Business Analyst portfolio. The bot answers HR/recruiter questions about the candidate using local Markdown knowledge base files and DeepSeek's OpenAI-compatible chat API. It also supports professional dialogue on business analysis, product logic, system analysis, data analytics, KPI, processes, and MVP topics.

## MVP Scope

- Telegram portfolio question -> local knowledge search -> short business-style answer.
- Telegram professional question -> DeepSeek chat answer in Senior BA / Product Manager style.
- Commands: `/start`, `/help`, `/projects`, `/skills`, `/links`.
- Local knowledge base in `knowledge/*.md`.
- Simple in-memory history of the last 6 user messages.
- Logging for requests and errors.
- Docker-ready and safe for GitHub publication.

## Constraints

- Keep the architecture simple and file structure explicit.
- Do not add a database, vector store, admin panel, or complex RAG until there is a business need.
- Do not hardcode secrets.
- Knowledge base content must be treated as the only factual source for answers about the candidate, portfolio, experience, projects, skills, and links.
- Professional answers may use the model's general knowledge, but must not invent facts about the candidate.
- Prefer minimal diffs and avoid unrelated refactoring.

## Before Publication

- Replace demo knowledge base content with real candidate facts.
- Verify all links in `knowledge/links.md`.
- Put real tokens only in local `.env`, never in Git.
