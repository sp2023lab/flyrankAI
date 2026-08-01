from __future__ import annotations

from statistics import mean

from app.models import (
    AnswerEvaluation,
    Difficulty,
    InterviewQuestion,
    NextAction,
    NoteMatch,
    QuestionResult,
    SessionReport,
)


class MockProvider:
    """Deterministic provider for tests and setup verification; not for final recording."""

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
    ) -> InterviewQuestion:
        excerpt = context[0].excerpt if context else "No matching note was found."
        if question_number == 1:
            question = (
                "In your FastAPI WebSocket stock ticker, how did persistent bidirectional "
                "communication change the design compared with a normal REST endpoint?"
            )
            category = "websockets"
        else:
            question = (
                "How did the Repository and Unit of Work patterns separate database access "
                "from transaction control in your async SQLAlchemy work?"
            )
            category = "databases"
        return InterviewQuestion(
            question=question,
            category=category,
            difficulty=difficulty,
            grounding_summary=excerpt[:220],
        )

    def evaluate_answer(
        self,
        *,
        question: InterviewQuestion,
        answer: str,
        context: list[NoteMatch],
        question_number: int,
        total_questions: int,
    ) -> AnswerEvaluation:
        answer_lower = answer.lower()
        relevant_terms = {
            "websockets": ["persistent", "bidirectional", "connection", "async"],
            "databases": ["repository", "transaction", "commit", "rollback", "unit of work"],
        }.get(question.category.lower(), [])
        hits = sum(term in answer_lower for term in relevant_terms)
        score = max(1, min(5, 1 + hits))
        next_action = (
            NextAction.END_SESSION
            if question_number >= total_questions
            else (NextAction.INCREASE_DIFFICULTY if score >= 4 else NextAction.SAME_TOPIC)
        )
        return AnswerEvaluation(
            score=score,
            correctness="The answer includes relevant technical concepts." if hits else "The answer lacks the core technical concept.",
            completeness="Coverage is proportionate to the number of key ideas included.",
            clarity="The response is understandable but can be made more structured.",
            evidence_quality="A concrete implementation detail would strengthen the answer.",
            main_improvement="State the design choice, why it was needed, and one concrete consequence.",
            next_action=next_action,
            follow_up_question=None,
        )

    def generate_report(self, results: list[QuestionResult]) -> SessionReport:
        average = mean(result.evaluation.score for result in results)
        strongest = [
            result.question.category
            for result in sorted(
                results, key=lambda item: item.evaluation.score, reverse=True
            )[:2]
        ]
        weakest = [
            result.question.category
            for result in sorted(results, key=lambda item: item.evaluation.score)[:2]
        ]
        return SessionReport(
            average_score=round(average, 2),
            strongest_areas=strongest or ["No clear strength yet"],
            improvement_areas=weakest or ["More evidence needed"],
            next_session_focus=f"Revisit {weakest[0] if weakest else 'technical explanation structure'} with deeper follow-ups.",
        )
