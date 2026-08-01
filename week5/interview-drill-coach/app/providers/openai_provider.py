from __future__ import annotations

import json
import os

from openai import OpenAI

from app.models import (
    AnswerEvaluation,
    Difficulty,
    InterviewQuestion,
    NoteMatch,
    QuestionResult,
    SessionReport,
)
from app.prompts import EVALUATION_SYSTEM, QUESTION_SYSTEM, REPORT_SYSTEM


class OpenAIProvider:
    """Structured-output provider using the OpenAI Responses API."""

    def __init__(self, model: str):
        if not os.getenv("OPENAI_API_KEY"):
            raise RuntimeError(
                "OPENAI_API_KEY is missing. Copy .env.example to .env and add your key."
            )
        self.client = OpenAI()
        self.model = model

    def _parse(self, *, system: str, user: str, schema):
        response = self.client.responses.parse(
            model=self.model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            text_format=schema,
        )
        if response.output_parsed is None:
            raise RuntimeError("The model did not return a parsed structured response")
        return response.output_parsed

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
        payload = {
            "topic": topic,
            "difficulty": difficulty.value,
            "question_number": question_number,
            "total_questions": total_questions,
            "retrieved_notes": [item.model_dump() for item in context],
            "weak_topics": weak_topics,
            "previous_questions": [
                result.question.question for result in previous_results
            ],
        }
        return self._parse(
            system=QUESTION_SYSTEM,
            user=json.dumps(payload, indent=2),
            schema=InterviewQuestion,
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
        payload = {
            "question": question.model_dump(mode="json"),
            "candidate_answer": answer,
            "retrieved_notes": [item.model_dump() for item in context],
            "question_number": question_number,
            "total_questions": total_questions,
            "must_end_after_this_question": question_number >= total_questions,
        }
        return self._parse(
            system=EVALUATION_SYSTEM,
            user=json.dumps(payload, indent=2),
            schema=AnswerEvaluation,
        )

    def generate_report(self, results: list[QuestionResult]) -> SessionReport:
        return self._parse(
            system=REPORT_SYSTEM,
            user=json.dumps(
                [result.model_dump(mode="json") for result in results], indent=2
            ),
            schema=SessionReport,
        )
