from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    provider: str
    openai_model: str
    data_dir: Path
    progress_file: Path


def load_settings() -> Settings:
    load_dotenv()
    project_root = Path(__file__).resolve().parents[1]
    data_dir = Path(os.getenv("AGENT_DATA_DIR", project_root / "data"))
    progress_file = Path(
        os.getenv("AGENT_PROGRESS_FILE", data_dir / "progress.json")
    )
    return Settings(
        provider=os.getenv("AGENT_PROVIDER", "openai").strip().lower(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.6").strip(),
        data_dir=data_dir,
        progress_file=progress_file,
    )
