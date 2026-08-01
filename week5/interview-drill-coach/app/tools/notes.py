from __future__ import annotations

import re
from collections import Counter
from pathlib import Path

from app.models import NoteMatch


_TOKEN_RE = re.compile(r"[a-zA-Z0-9+#.-]+")
_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how",
    "i", "in", "is", "it", "of", "on", "or", "that", "the", "this", "to",
    "was", "were", "what", "when", "with", "you", "your",
}


def _tokens(text: str) -> list[str]:
    return [
        token.lower()
        for token in _TOKEN_RE.findall(text)
        if token.lower() not in _STOP_WORDS and len(token) > 1
    ]


def _chunk_markdown(text: str) -> list[str]:
    """Create paragraph chunks while carrying the nearest Markdown heading.

    This handles both headings followed immediately by body text and headings separated
    by blank lines.
    """
    chunks: list[str] = []
    current_heading = ""
    body_lines: list[str] = []

    def flush() -> None:
        if not body_lines:
            return
        body = " ".join(line.strip() for line in body_lines if line.strip()).strip()
        body_lines.clear()
        if body:
            prefix = f"{current_heading}: " if current_heading else ""
            chunks.append(prefix + body)

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            flush()
            current_heading = stripped.lstrip("# ").strip()
        elif not stripped:
            flush()
        else:
            body_lines.append(stripped)
    flush()
    return chunks


class NotesTool:
    """Read-only keyword retrieval over local Markdown/text documents."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir

    def _documents(self) -> list[Path]:
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        return sorted(
            path
            for path in self.data_dir.iterdir()
            if path.suffix.lower() in {".md", ".txt"} and path.name != "progress.json"
        )

    def search(self, query: str, limit: int = 3) -> list[NoteMatch]:
        query_tokens = Counter(_tokens(query))
        if not query_tokens:
            return []

        matches: list[NoteMatch] = []
        for path in self._documents():
            text = path.read_text(encoding="utf-8")
            for chunk in _chunk_markdown(text):
                chunk_tokens = Counter(_tokens(chunk))
                overlap = sum(
                    min(count, chunk_tokens[token])
                    for token, count in query_tokens.items()
                )
                if overlap == 0:
                    continue
                phrase_bonus = 1.5 if query.lower() in chunk.lower() else 0.0
                density = overlap / max(len(chunk_tokens), 1)
                score = float(overlap + phrase_bonus + density)
                matches.append(
                    NoteMatch(source=path.name, excerpt=chunk[:900], score=score)
                )

        matches.sort(key=lambda item: (-item.score, item.source, item.excerpt))
        return matches[:limit]
