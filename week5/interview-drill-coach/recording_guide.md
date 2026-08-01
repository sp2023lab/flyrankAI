# Raw FL-07 Run Capture — 2-Minute Plan

The recording must be made locally and remain unedited.

## Before recording

1. Install dependencies and configure `.env`.
2. Run `pytest` and one private live session.
3. Reset `data/progress.json` only if you want a clean demo; do not edit anything during the recording.
4. Open a terminal at the project root.

## Recording command

```bash
python -m app.main --provider openai --topic "backend projects" --difficulty medium --questions 2
```

## Suggested timeline

- **0:00–0:10** — Show the command and start the agent.
- **0:10–0:25** — Show `interview_get_progress` and `interview_search_notes` output.
- **0:25–0:55** — Answer question one naturally; show score and saved-result tool output.
- **0:55–1:30** — Answer question two; show the second evaluation.
- **1:30–1:55** — Show `interview_end_session` and the final report.
- **1:55–2:00** — Show clean program termination.

## Suitable answer material

For the WebSocket question, mention persistent full-duplex communication, server push, connection lifecycle and async broadcasting.

For the Repository/Unit of Work question, explain that repositories encapsulate data access while the Unit of Work owns the session and transaction boundary, including commit/rollback.

Do not paste answers during the recording; type or speak naturally so the capture remains credible.
