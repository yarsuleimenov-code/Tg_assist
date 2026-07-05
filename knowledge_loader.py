import re
from dataclasses import dataclass
from pathlib import Path


DEFAULT_KNOWLEDGE_FILES = (
    "profile.md",
    "projects.md",
    "skills.md",
    "case_studies.md",
    "links.md",
)


@dataclass(frozen=True)
class KnowledgeDocument:
    path: Path
    title: str
    content: str


@dataclass(frozen=True)
class KnowledgeMatch:
    document: KnowledgeDocument
    score: int


class KnowledgeBase:
    def __init__(self, root_dir: str = "knowledge") -> None:
        self.root_dir = Path(root_dir)
        self.documents: list[KnowledgeDocument] = []

    def load(self) -> None:
        documents = []
        for file_name in DEFAULT_KNOWLEDGE_FILES:
            path = self.root_dir / file_name
            if not path.exists():
                continue

            content = path.read_text(encoding="utf-8").strip()
            if not content:
                continue

            title = self._extract_title(content) or file_name
            documents.append(KnowledgeDocument(path=path, title=title, content=content))

        self.documents = documents

    def search(self, query: str, limit: int = 4) -> list[KnowledgeMatch]:
        tokens = self._tokens(query)
        if not tokens:
            return []

        matches = []
        for document in self.documents:
            title = document.title.lower()
            content = document.content.lower()
            score = 0

            for token in tokens:
                if token in title:
                    score += 4
                score += content.count(token)

            if score > 0:
                matches.append(KnowledgeMatch(document=document, score=score))

        return sorted(matches, key=lambda item: item.score, reverse=True)[:limit]

    def build_context(self, matches: list[KnowledgeMatch], max_chars: int) -> str:
        parts = []
        total = 0

        for match in matches:
            block = (
                f"Источник: {match.document.path.as_posix()}\n"
                f"Раздел: {match.document.title}\n"
                f"{match.document.content}"
            )
            remaining = max_chars - total
            if remaining <= 0:
                break

            if len(block) > remaining:
                block = block[:remaining]

            parts.append(block)
            total += len(block)

        return "\n\n---\n\n".join(parts)

    def get_document_text(self, file_name: str) -> str:
        for document in self.documents:
            if document.path.name == file_name:
                return document.content
        return "В доступных материалах нет информации по этому вопросу."

    @staticmethod
    def _extract_title(content: str) -> str | None:
        for line in content.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return None

    @staticmethod
    def _tokens(text: str) -> set[str]:
        raw_tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9_+-]+", text.lower())
        return {token for token in raw_tokens if len(token) >= 3}
