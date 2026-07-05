# Project Instructions

## Goal

MVP Telegram AI assistant for a Business Analyst portfolio. The bot answers HR/recruiter questions using only local Markdown knowledge base files and DeepSeek's OpenAI-compatible chat API.

## MVP Scope

- Telegram text question -> local knowledge search -> short business-style answer.
- Commands: `/start`, `/help`, `/projects`, `/skills`, `/links`.
- Local knowledge base in `knowledge/*.md`.
- Simple in-memory history of the last 6 user messages.
- Logging for requests and errors.
- Docker-ready and safe for GitHub publication.

## Constraints

- Keep the architecture simple and file structure explicit.
- Do not add a database, vector store, admin panel, or complex RAG until there is a business need.
- Do not hardcode secrets.
- Knowledge base content must be treated as the only factual source for answers.
- Prefer minimal diffs and avoid unrelated refactoring.

## Before Publication

- Replace demo knowledge base content with real candidate facts.
- Verify all links in `knowledge/links.md`.
- Put real tokens only in local `.env`, never in Git.
