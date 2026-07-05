import re
from dataclasses import dataclass
from pathlib import Path


DEFAULT_KNOWLEDGE_FILES = (
    "profile.md",
    "projects.md",
    "skills.md",
    "case_studies.md",
    "evidence.md",
    "links.md",
)

STOP_WORDS = {
    "как",
    "что",
    "где",
    "для",
    "или",
    "это",
    "есть",
    "про",
    "при",
    "чем",
    "кто",
    "the",
    "and",
    "for",
    "with",
}

SYNONYMS = {
    "склад": ("warehouse", "loading", "логистика"),
    "складской": ("warehouse", "loading", "логистика"),
    "загрузка": ("loading", "warehouse", "trip"),
    "отгрузка": ("loading", "warehouse", "trip"),
    "приемка": ("unloading", "warehouse", "trip"),
    "калькулятор": ("calculator", "smartquote", "zaberman", "pricing"),
    "расчет": ("calculator", "pricing", "quote"),
    "расчёт": ("calculator", "pricing", "quote"),
    "коммерческое": ("quote", "smartquote", "pricing"),
    "предложение": ("quote", "smartquote", "pricing"),
    "клиенты": ("client", "crm", "tracker"),
    "клиент": ("client", "crm", "tracker"),
    "меню": ("family menu", "foodtech", "planning"),
    "еда": ("family menu", "foodtech"),
    "дашборд": ("dashboard", "analytics", "bi"),
    "отчет": ("reporting", "analytics", "dashboard"),
    "отчёт": ("reporting", "analytics", "dashboard"),
    "аналитика": ("analytics", "dashboard", "olap"),
    "витрина": ("olap", "analytics", "dashboard"),
    "данные": ("data", "analytics", "olap"),
    "mvp": ("product", "hypothesis", "scope"),
    "требования": ("requirements", "business analysis", "scope"),
}


@dataclass(frozen=True)
class KnowledgeDocument:
    path: Path
    title: str
    content: str


@dataclass(frozen=True)
class KnowledgeChunk:
    source_file: str
    title: str
    content: str
    project: str
    role: str
    domain: str


@dataclass(frozen=True)
class KnowledgeMatch:
    chunk: KnowledgeChunk
    score: int


class KnowledgeBase:
    def __init__(self, root_dir: str = "knowledge") -> None:
        self.root_dir = Path(root_dir)
        self.documents: list[KnowledgeDocument] = []
        self.chunks: list[KnowledgeChunk] = []

    def load(self) -> None:
        documents = []
        chunks = []
        for file_name in DEFAULT_KNOWLEDGE_FILES:
            path = self.root_dir / file_name
            if not path.exists():
                continue

            content = path.read_text(encoding="utf-8").strip()
            if not content:
                continue

            title = self._extract_title(content) or file_name
            document = KnowledgeDocument(path=path, title=title, content=content)
            documents.append(document)
            chunks.extend(self._build_chunks(document))

        self.documents = documents
        self.chunks = chunks

    def search(self, query: str, limit: int = 5) -> list[KnowledgeMatch]:
        tokens = self._expand_tokens(self._tokens(query))
        if not tokens:
            return []

        matches = []
        for chunk in self.chunks:
            searchable_title = chunk.title.lower()
            searchable_meta = " ".join(
                [chunk.project, chunk.role, chunk.domain, chunk.source_file]
            ).lower()
            searchable_content = chunk.content.lower()
            score = 0

            for token in tokens:
                if token in searchable_title:
                    score += 5
                if token in searchable_meta:
                    score += 6
                score += searchable_content.count(token)

            if score > 0:
                matches.append(KnowledgeMatch(chunk=chunk, score=score))

        return sorted(matches, key=lambda item: item.score, reverse=True)[:limit]

    def build_context(self, matches: list[KnowledgeMatch], max_chars: int) -> str:
        parts = []
        total = 0

        for match in matches:
            chunk = match.chunk
            block = (
                f"Источник: {chunk.source_file}\n"
                f"Раздел: {chunk.title}\n"
                f"Metadata: project={chunk.project}; role={chunk.role}; domain={chunk.domain}\n"
                f"{chunk.content}"
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

    def build_context_from_files(self, file_names: tuple[str, ...], max_chars: int) -> str:
        matches = [
            KnowledgeMatch(chunk=chunk, score=1)
            for chunk in self.chunks
            if chunk.source_file in file_names
        ]
        return self.build_context(matches, max_chars=max_chars)

    def _build_chunks(self, document: KnowledgeDocument) -> list[KnowledgeChunk]:
        sections = self._split_sections(document.content, document.title)
        chunks = []

        for title, content in sections:
            for part in self._split_large_section(content):
                project = self._infer_project(document.path.name, title, part)
                role = self._infer_role(document.path.name, title, part)
                domain = self._infer_domain(title, part)
                chunks.append(
                    KnowledgeChunk(
                        source_file=document.path.name,
                        title=title,
                        content=part.strip(),
                        project=project,
                        role=role,
                        domain=domain,
                    )
                )

        return chunks

    @staticmethod
    def _split_sections(content: str, default_title: str) -> list[tuple[str, str]]:
        sections = []
        current_title = default_title
        current_lines = []

        for line in content.splitlines():
            if line.startswith("## "):
                if current_lines:
                    sections.append((current_title, "\n".join(current_lines).strip()))
                current_title = line[3:].strip()
                current_lines = [line]
                continue

            if line.startswith("# ") and not current_lines:
                current_title = line[2:].strip()

            current_lines.append(line)

        if current_lines:
            sections.append((current_title, "\n".join(current_lines).strip()))

        return [(title, body) for title, body in sections if body]

    @staticmethod
    def _split_large_section(content: str, max_chars: int = 1800) -> list[str]:
        if len(content) <= max_chars:
            return [content]

        parts = []
        current = []
        current_len = 0
        for paragraph in re.split(r"\n\s*\n", content):
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            paragraph_len = len(paragraph) + 2
            if current and current_len + paragraph_len > max_chars:
                parts.append("\n\n".join(current))
                current = []
                current_len = 0
            current.append(paragraph)
            current_len += paragraph_len

        if current:
            parts.append("\n\n".join(current))

        return parts

    @staticmethod
    def _extract_title(content: str) -> str | None:
        for line in content.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return None

    @staticmethod
    def _infer_project(source_file: str, title: str, content: str) -> str:
        if source_file in {"profile.md", "skills.md", "links.md"}:
            return source_file.replace(".md", "")

        clean_title = re.sub(r"^\d+[\).\s-]*", "", title).strip("# ").strip()
        if clean_title:
            return clean_title[:80]

        text = content.lower()
        known_projects = (
            "smartquote",
            "zaberman",
            "warehouse",
            "loading control",
            "client tracker",
            "family menu",
            "ys-analytics",
            "iitu olap",
        )
        for project in known_projects:
            if project in text:
                return project
        return "portfolio"

    @staticmethod
    def _infer_role(source_file: str, title: str, content: str) -> str:
        text = f"{source_file} {title} {content}".lower()
        if "product" in text or "mvp" in text:
            return "Business Analyst / Product Analyst"
        if "system" in text or "api" in text or "integration" in text:
            return "Business Analyst / System Analyst"
        if "dashboard" in text or "olap" in text or "analytics" in text:
            return "Business Analyst / Data Analyst"
        return "Business Analyst"

    @staticmethod
    def _infer_domain(title: str, content: str) -> str:
        text = f"{title} {content}".lower()
        domains = (
            ("warehouse", "warehouse / logistics"),
            ("склад", "warehouse / logistics"),
            ("логист", "warehouse / logistics"),
            ("loading", "logistics / operations"),
            ("client", "CRM / client tracking"),
            ("crm", "CRM / client tracking"),
            ("family menu", "foodtech / family planning"),
            ("menu", "foodtech / family planning"),
            ("quote", "sales / pricing"),
            ("olap", "analytics / education"),
            ("dashboard", "analytics / BI"),
            ("api", "system integration"),
        )
        for marker, domain in domains:
            if marker in text:
                return domain
        return "business analysis"

    @staticmethod
    def _tokens(text: str) -> set[str]:
        raw_tokens = re.findall(r"[a-zA-Zа-яА-ЯёЁ0-9_+-]+", text.lower())
        return {token for token in raw_tokens if len(token) >= 3 and token not in STOP_WORDS}

    @staticmethod
    def _expand_tokens(tokens: set[str]) -> set[str]:
        expanded = set(tokens)
        for token in tokens:
            expanded.update(SYNONYMS.get(token, ()))
        return expanded
