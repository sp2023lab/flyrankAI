from __future__ import annotations

from typing import Protocol

from app.models import (
    AnswerEvaluation,
    Difficulty,
    InterviewQuestion,
    NoteMatch,
    QuestionResult,
    SessionReport,
)


class InterviewProvider(Protocol):
    def generate_question(
        self,
        *,
        topic: str,
        difficulty: Difficulty,
        question_number: int,
        total_questions: int,
        context: list[NoteMatch],
        weak_topics: list[tuple[str, float]],
        previous_results: list[QuestionResult],
    ) -> InterviewQuestion: ...

    def evaluate_answer(
        self,
        *,
        question: InterviewQuestion,
        answer: str,
        context: list[NoteMatch],
        question_number: int,
        total_questions: int,
    ) -> AnswerEvaluation: ...

    def generate_report(self, results: list[QuestionResult]) -> SessionReport: ...
