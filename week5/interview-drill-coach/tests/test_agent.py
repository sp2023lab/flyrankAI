from pathlib import Path

from app.agent import InterviewAgent
from app.models import Difficulty, SessionRequest
from app.providers.mock_provider import MockProvider
from app.tools.notes import NotesTool
from app.tools.progress import ProgressStore


def test_agent_completes_two_question_loop(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    (data_dir / "notes.md").write_text(
        "# WebSockets\nPersistent bidirectional async connections.\n\n"
        "# Databases\nRepository pattern and Unit of Work commit rollback transaction.",
        encoding="utf-8",
    )
    outputs: list[str] = []
    answers = iter(
        [
            "It keeps a persistent bidirectional async connection.",
            "The repository performs data access while the unit of work owns commit and rollback.",
        ]
    )
    agent = InterviewAgent(
        provider=MockProvider(),
        notes=NotesTool(data_dir),
        progress=ProgressStore(data_dir / "progress.json"),
        output=outputs.append,
    )
    report = agent.run_session(
        SessionRequest(topic="backend projects", difficulty=Difficulty.MEDIUM, question_count=2),
        input_fn=lambda _: next(answers),
    )
    assert report.average_score >= 1
    assert any("interview_search_notes" in line for line in outputs)
    assert any("interview_end_session" in line for line in outputs)
    saved = agent.progress.get_progress()
    assert saved.sessions[0].status == "completed"
    assert len(saved.sessions[0].results) == 2
