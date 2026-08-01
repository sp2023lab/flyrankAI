# Interview Drill Coach — FL-07 MVP

A single-agent command-line application that runs adaptive software-engineering interview practice grounded in local CV, project and technical-note files.

## Core workflow

1. Read prior topic scores from `data/progress.json`.
2. Search local Markdown files for relevant evidence.
3. Ask one grounded interview question.
4. Evaluate the user's answer with a fixed 1–5 rubric.
5. Save the result immediately.
6. Repeat until the requested count is reached.
7. Generate and save a final session report.

The terminal prints every tool invocation so the FL-07 recording visibly demonstrates the live file and progress connections.

## Requirements

- Python 3.11+
- An OpenAI API key for the final live run

## Setup

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Open `.env`, replace `replace_with_your_key`, and choose a model available to your API project if the default is unavailable.

## Run the live agent

```bash
python -m app.main --provider openai --topic "backend projects" --difficulty medium --questions 2
```

## Verify setup without API usage

```bash
python -m app.main --provider mock --topic "backend projects" --difficulty medium --questions 2
```

The mock provider verifies the full workflow and local tools, but the final FL-07 screen recording should use `--provider openai`.

## Run tests

```bash
pytest
```

## Connected data sources

- `data/cv.md`
- `data/projects.md`
- `data/technical_notes.md`
- `data/behavioural_examples.md`
- `data/progress.json`

The notes are read-only. The agent writes only to its dedicated progress file.

## Guardrails

- Project-specific questions must be grounded in retrieved notes.
- Source documents remain read-only.
- Answers use a fixed scoring rubric.
- Question count is limited to 1–10.
- The agent cannot send messages, edit a CV, submit applications or perform external actions.
- New experience is not silently treated as verified background information.

## FL-06 deviations and deliberate cuts

- Used keyword retrieval rather than embeddings/vector search because the local corpus is small and the MVP needs one reliable end-to-end path.
- Used JSON rather than SQLite to minimise setup and keep progress human-readable.
- Kept the interface as a CLI; FastAPI/UI, voice, multi-agent orchestration and analytics were deferred.
- The four FL-06 tool responsibilities remain present: note search, progress retrieval, result saving and session completion.

## Known limitations

- Retrieval is lexical, so semantically related wording without shared terms may be missed.
- Scoring quality depends on the selected LLM.
- No authentication is required because this is a local personal MVP.
- Interrupted live sessions remain marked `in_progress`; cleanup is a later enhancement.
