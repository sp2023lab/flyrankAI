from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class NextAction(str, Enum):
    FOLLOW_UP = "follow_up"
    INCREASE_DIFFICULTY = "increase_difficulty"
    SAME_TOPIC = "same_topic"
    CHANGE_TOPIC = "change_topic"
    END_SESSION = "end_session"


class NoteMatch(BaseModel):
    source: str
    excerpt: str
    score: float = Field(ge=0)


class InterviewQuestion(BaseModel):
    question: str = Field(min_length=5)
    category: str = Field(min_length=2)
    difficulty: Difficulty
    grounding_summary: str = Field(
        description="Brief statement of which retrieved facts informed the question."
    )


class AnswerEvaluation(BaseModel):
    score: int = Field(ge=1, le=5)
    correctness: str
    completeness: str
    clarity: str
    evidence_quality: str
    main_improvement: str
    next_action: NextAction
    follow_up_question: str | None = None


class QuestionResult(BaseModel):
    question_number: int = Field(ge=1)
    question: InterviewQuestion
    answer: str
    evaluation: AnswerEvaluation
    saved_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class SessionReport(BaseModel):
    average_score: float = Field(ge=1, le=5)
    strongest_areas: list[str] = Field(min_length=1, max_length=3)
    improvement_areas: list[str] = Field(min_length=1, max_length=3)
    next_session_focus: str


class SessionRecord(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid4()))
    started_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    completed_at: str | None = None
    topic: str
    difficulty: Difficulty
    requested_questions: int = Field(ge=1, le=10)
    results: list[QuestionResult] = Field(default_factory=list)
    report: SessionReport | None = None
    status: Literal["in_progress", "completed"] = "in_progress"


class ProgressData(BaseModel):
    sessions: list[SessionRecord] = Field(default_factory=list)
    topic_scores: dict[str, list[int]] = Field(default_factory=dict)


class SessionRequest(BaseModel):
    topic: str = Field(min_length=2)
    difficulty: Difficulty = Difficulty.MEDIUM
    question_count: int = Field(default=2, ge=1, le=10)
