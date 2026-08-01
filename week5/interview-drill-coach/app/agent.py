from __future__ import annotations

from collections.abc import Callable

from app.models import QuestionResult, SessionRecord, SessionReport, SessionRequest
from app.providers.base import InterviewProvider
from app.tools.notes import NotesTool
from app.tools.progress import ProgressStore


class InterviewAgent:
    def __init__(
        self,
        *,
        provider: InterviewProvider,
        notes: NotesTool,
        progress: ProgressStore,
        output: Callable[[str], None] = print,
    ):
        self.provider = provider
        self.notes = notes
        self.progress = progress
        self.output = output

    def run_session(
        self,
        request: SessionRequest,
        *,
        input_fn: Callable[[str], str] = input,
    ) -> SessionReport:
        session = SessionRecord(
            topic=request.topic,
            difficulty=request.difficulty,
            requested_questions=request.question_count,
        )
        self.progress.start_session(session)
        weak_topics = self.progress.weak_topics()
        self.output(f"\nSession {session.session_id[:8]} started")
        self.output(
            f"Topic: {request.topic} | Difficulty: {request.difficulty.value} | "
            f"Questions: {request.question_count}"
        )
        if weak_topics:
            formatted = ", ".join(f"{topic} ({avg:.1f}/5)" for topic, avg in weak_topics)
            self.output(f"[tool] interview_get_progress -> weak topics: {formatted}")
        else:
            self.output("[tool] interview_get_progress -> no previous scores")

        results: list[QuestionResult] = []
        for number in range(1, request.question_count + 1):
            query = self._retrieval_query(request.topic, weak_topics, results)
            context = self.notes.search(query, limit=3)
            sources = ", ".join(sorted({match.source for match in context})) or "none"
            self.output(
                f"\n[tool] interview_search_notes -> {len(context)} matches from {sources}"
            )

            question = self.provider.generate_question(
                topic=request.topic,
                difficulty=request.difficulty,
                question_number=number,
                total_questions=request.question_count,
                context=context,
                weak_topics=weak_topics,
                previous_results=results,
            )
            self.output(f"\nQuestion {number}/{request.question_count} [{question.category}]")
            self.output(question.question)

            answer = self._read_non_empty_answer(input_fn)
            evaluation = self.provider.evaluate_answer(
                question=question,
                answer=answer,
                context=context,
                question_number=number,
                total_questions=request.question_count,
            )
            result = QuestionResult(
                question_number=number,
                question=question,
                answer=answer,
                evaluation=evaluation,
            )
            results.append(result)
            self.progress.save_result(session.session_id, result)
            self.output(
                f"[tool] interview_save_result -> saved score {evaluation.score}/5"
            )
            self._display_evaluation(evaluation)

        report = self.provider.generate_report(results)
        self.progress.complete_session(session.session_id, report)
        self.output("\n[tool] interview_end_session -> report generated and session completed")
        self._display_report(report)
        return report

    @staticmethod
    def _retrieval_query(topic, weak_topics, results) -> str:
        components = [topic]
        if weak_topics:
            components.append(weak_topics[0][0])
        if results:
            components.append(results[-1].question.category)
        return " ".join(components)

    @staticmethod
    def _read_non_empty_answer(input_fn: Callable[[str], str]) -> str:
        for _ in range(2):
            answer = input_fn("Your answer: ").strip()
            if answer:
                return answer
            print("Please enter an answer; an empty response cannot be evaluated.")
        return "No answer provided."

    def _display_evaluation(self, evaluation) -> None:
        self.output(f"Score: {evaluation.score}/5")
        self.output(f"Correctness: {evaluation.correctness}")
        self.output(f"Completeness: {evaluation.completeness}")
        self.output(f"Clarity: {evaluation.clarity}")
        self.output(f"Evidence: {evaluation.evidence_quality}")
        self.output(f"Main improvement: {evaluation.main_improvement}")
        self.output(f"Next action: {evaluation.next_action.value}")

    def _display_report(self, report: SessionReport) -> None:
        self.output("\n=== Session report ===")
        self.output(f"Average score: {report.average_score:.2f}/5")
        self.output("Strongest areas: " + "; ".join(report.strongest_areas))
        self.output("Improvement areas: " + "; ".join(report.improvement_areas))
        self.output("Next focus: " + report.next_session_focus)
