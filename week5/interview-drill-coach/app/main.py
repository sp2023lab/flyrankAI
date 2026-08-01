from __future__ import annotations

import argparse
import sys

from pydantic import ValidationError

from app.agent import InterviewAgent
from app.config import load_settings
from app.models import Difficulty, SessionRequest
from app.providers.mock_provider import MockProvider
from app.tools.notes import NotesTool
from app.tools.progress import ProgressStore


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Adaptive interview-practice agent")
    parser.add_argument("--provider", choices=["openai", "mock"])
    parser.add_argument("--topic")
    parser.add_argument("--difficulty", choices=[item.value for item in Difficulty])
    parser.add_argument("--questions", type=int)
    return parser


def _prompt(value: str | None, label: str, default: str) -> str:
    if value:
        return value
    entered = input(f"{label} [{default}]: ").strip()
    return entered or default


def main() -> int:
    args = _parser().parse_args()
    settings = load_settings()
    provider_name = args.provider or settings.provider

    try:
        request = SessionRequest(
            topic=_prompt(args.topic, "Topic", "backend projects"),
            difficulty=Difficulty(
                _prompt(args.difficulty, "Difficulty", Difficulty.MEDIUM.value).lower()
            ),
            question_count=int(
                _prompt(
                    str(args.questions) if args.questions is not None else None,
                    "Number of questions",
                    "2",
                )
            ),
        )
        if provider_name == "mock":
            provider = MockProvider()
        else:
            from app.providers.openai_provider import OpenAIProvider

            provider = OpenAIProvider(settings.openai_model)
        agent = InterviewAgent(
            provider=provider,
            notes=NotesTool(settings.data_dir),
            progress=ProgressStore(settings.progress_file),
        )
        agent.run_session(request)
        return 0
    except (ValidationError, ValueError) as exc:
        print(f"Invalid session configuration: {exc}", file=sys.stderr)
        return 2
    except (FileNotFoundError, RuntimeError) as exc:
        print(f"Setup error: {exc}", file=sys.stderr)
        return 3
    except KeyboardInterrupt:
        print("\nSession cancelled by user.")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
