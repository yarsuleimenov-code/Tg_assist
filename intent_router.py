import re
from dataclasses import dataclass
from enum import Enum


class Intent(str, Enum):
    PORTFOLIO = "portfolio_question"
    PROFESSIONAL = "professional_question"
    CLARIFICATION = "clarification_needed"
    OUT_OF_SCOPE = "out_of_scope"


@dataclass(frozen=True)
class IntentResult:
    intent: Intent
    confidence: float
    topic: str
    reason: str
    needs_llm: bool = False


PORTFOLIO_TERMS = (
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
    "olap",
    "iitu",
)

GENERAL_PORTFOLIO_TERMS = (
    "что ты знаешь",
    "расскажи о себе",
    "расскажи о кандидате",
    "расскажи про кандидата",
    "расскажи о ярославе",
    "кто такой",
    "кто кандидат",
    "о кандидате",
    "о ярославе",
    "чем полезен кандидат",
    "что умеет кандидат",
    "почему его стоит",
    "профиль кандидата",
)

PROFESSIONAL_TERMS = (
    "business analysis",
    "business analyst",
    "бизнес-анализ",
    "бизнес анализ",
    "требован",
    "mvp",
    "scope",
    "user story",
    "use case",
    "acceptance criteria",
    "backlog",
    "roadmap",
    "kpi",
    "метрик",
    "dashboard",
    "дашборд",
    "процесс",
    "as-is",
    "to-be",
    "bpmn",
    "uml",
    "api",
    "data contract",
    "интеграц",
    "аналитик",
    "продукт",
    "гипотез",
    "риск",
    "stakeholder",
    "стейкхолдер",
    "custdev",
    "moscow",
)

OUT_OF_SCOPE_TERMS = (
    "погода",
    "курс валют",
    "новости",
    "рецепт",
    "анекдот",
    "фильм",
    "музыка",
    "медицина",
    "диагноз",
    "юридическая консультация",
    "инвестиционный совет",
)

CLARIFICATION_TERMS = (
    "помоги",
    "как лучше",
    "что делать",
    "с чего начать",
    "подскажи",
    "объясни",
)


def route_intent(text: str) -> IntentResult:
    normalized = _normalize(text)
    tokens = _tokens(normalized)

    if not normalized:
        return IntentResult(
            intent=Intent.CLARIFICATION,
            confidence=1.0,
            topic="empty_question",
            reason="empty message",
        )

    if _contains_any(normalized, OUT_OF_SCOPE_TERMS):
        return IntentResult(
            intent=Intent.OUT_OF_SCOPE,
            confidence=0.9,
            topic=_first_match(normalized, OUT_OF_SCOPE_TERMS) or "out_of_scope",
            reason="matched out-of-scope term",
        )

    if len(tokens) <= 2 and not _contains_any(normalized, PORTFOLIO_TERMS + PROFESSIONAL_TERMS):
        return IntentResult(
            intent=Intent.CLARIFICATION,
            confidence=0.9,
            topic="short_question",
            reason="too short to route",
        )

    if is_general_portfolio_question(normalized) or _contains_any(normalized, PORTFOLIO_TERMS):
        return IntentResult(
            intent=Intent.PORTFOLIO,
            confidence=0.86,
            topic=_first_match(normalized, PORTFOLIO_TERMS + GENERAL_PORTFOLIO_TERMS) or "portfolio",
            reason="matched portfolio term",
        )

    if _contains_any(normalized, PROFESSIONAL_TERMS):
        return IntentResult(
            intent=Intent.PROFESSIONAL,
            confidence=0.82,
            topic=_first_match(normalized, PROFESSIONAL_TERMS) or "professional",
            reason="matched BA professional term",
        )

    if _contains_any(normalized, CLARIFICATION_TERMS) and len(tokens) <= 5:
        return IntentResult(
            intent=Intent.CLARIFICATION,
            confidence=0.78,
            topic="unclear_context",
            reason="generic request without context",
        )

    return IntentResult(
        intent=Intent.PROFESSIONAL,
        confidence=0.42,
        topic=_topic_from_tokens(tokens),
        reason="low-confidence fallback",
        needs_llm=True,
    )


def parse_llm_intent(value: str, fallback: IntentResult) -> IntentResult:
    normalized = _normalize(value)
    mapping = {
        Intent.PORTFOLIO.value: Intent.PORTFOLIO,
        Intent.PROFESSIONAL.value: Intent.PROFESSIONAL,
        Intent.CLARIFICATION.value: Intent.CLARIFICATION,
        Intent.OUT_OF_SCOPE.value: Intent.OUT_OF_SCOPE,
    }
    for label, intent in mapping.items():
        if label in normalized:
            return IntentResult(
                intent=intent,
                confidence=0.68,
                topic=fallback.topic,
                reason="llm fallback router",
                needs_llm=False,
            )
    return fallback


def is_general_portfolio_question(text: str) -> bool:
    normalized = _normalize(text)
    return _contains_any(normalized, GENERAL_PORTFOLIO_TERMS)


def _contains_any(text: str, terms: tuple[str, ...]) -> bool:
    return any(term in text for term in terms)


def _first_match(text: str, terms: tuple[str, ...]) -> str | None:
    for term in terms:
        if term in text:
            return term
    return None


def _normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9_+-]+", text.lower())


def _topic_from_tokens(tokens: list[str]) -> str:
    meaningful = [token for token in tokens if len(token) >= 4]
    return " ".join(meaningful[:3]) if meaningful else "unknown"
