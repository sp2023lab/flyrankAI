from pathlib import Path

from app.models import (
    AnswerEvaluation,
    Difficulty,
    InterviewQuestion,
    NextAction,
    QuestionResult,
    SessionRecord,
    SessionReport,
)
from app.tools.progress import ProgressStore


def _result(score: int = 2) -> QuestionResult:
    return QuestionResult(
        question_number=1,
        question=InterviewQuestion(
            question="Explain transaction boundaries in a Unit of Work.",
            category="databases",
            difficulty=Difficulty.MEDIUM,
            grounding_summary="Repository and Unit of Work notes.",
        ),
        answer="The unit of work commits or rolls back.",
        evaluation=AnswerEvaluation(
            score=score,
            correctness="Mostly correct",
            completeness="Some gaps",
            clarity="Clear",
            evidence_quality="Needs example",
            main_improvement="Explain repository responsibility",
            next_action=NextAction.SAME_TOPIC,
        ),
    )


def test_progress_lifecycle(tmp_path: Path):
    store = ProgressStore(tmp_path / "progress.json")
    session = SessionRecord(
        topic="databases", difficulty=Difficulty.MEDIUM, requested_questions=1
    )
    store.start_session(session)
    store.save_result(session.session_id, _result())
    report = SessionReport(
        average_score=2,
        strongest_areas=["transaction boundary"],
        improvement_areas=["repository separation"],
        next_session_focus="Database patterns",
    )
    store.complete_session(session.session_id, report)

    data = store.get_progress()
    assert data.sessions[0].status == "completed"
    assert data.topic_scores["databases"] == [2]
    assert store.weak_topics()[0] == ("databases", 2.0)


def test_corrupt_progress_file_recovers_to_empty_store(tmp_path: Path):
    path = tmp_path / "progress.json"
    path.write_text("not valid json", encoding="utf-8")
    store = ProgressStore(path)
    assert store.get_progress().sessions == []
