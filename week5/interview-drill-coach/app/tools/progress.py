from __future__ import annotations

import json
from json import JSONDecodeError
from datetime import datetime, timezone
from pathlib import Path

from app.models import ProgressData, QuestionResult, SessionRecord, SessionReport


class ProgressStore:
    """JSON-backed progress tool with atomic writes."""

    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self._write(ProgressData())

    def _read(self) -> ProgressData:
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return ProgressData.model_validate(raw)
        except (JSONDecodeError, ValueError):
            backup = self.path.with_suffix(self.path.suffix + ".corrupt")
            counter = 1
            while backup.exists():
                backup = self.path.with_suffix(self.path.suffix + f".corrupt.{counter}")
                counter += 1
            self.path.replace(backup)
            empty = ProgressData()
            self._write(empty)
            return empty

    def _write(self, data: ProgressData) -> None:
        temporary = self.path.with_suffix(self.path.suffix + ".tmp")
        temporary.write_text(
            json.dumps(data.model_dump(mode="json"), indent=2),
            encoding="utf-8",
        )
        temporary.replace(self.path)

    def get_progress(self) -> ProgressData:
        return self._read()

    def weak_topics(self, limit: int = 3) -> list[tuple[str, float]]:
        data = self._read()
        averages = [
            (topic, sum(scores) / len(scores))
            for topic, scores in data.topic_scores.items()
            if scores
        ]
        return sorted(averages, key=lambda item: (item[1], item[0]))[:limit]

    def start_session(self, session: SessionRecord) -> None:
        data = self._read()
        data.sessions.append(session)
        self._write(data)

    def save_result(self, session_id: str, result: QuestionResult) -> None:
        data = self._read()
        session = self._find_session(data, session_id)
        if session.status != "in_progress":
            raise ValueError("Cannot add a result to a completed session")
        session.results.append(result)
        category = result.question.category.strip().lower()
        data.topic_scores.setdefault(category, []).append(result.evaluation.score)
        self._write(data)

    def complete_session(self, session_id: str, report: SessionReport) -> None:
        data = self._read()
        session = self._find_session(data, session_id)
        session.report = report
        session.status = "completed"
        session.completed_at = datetime.now(timezone.utc).isoformat()
        self._write(data)

    @staticmethod
    def _find_session(data: ProgressData, session_id: str) -> SessionRecord:
        for session in data.sessions:
            if session.session_id == session_id:
                return session
        raise KeyError(f"Unknown session: {session_id}")
