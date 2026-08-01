from pathlib import Path

from app.tools.notes import NotesTool


def test_search_returns_websocket_project_context(tmp_path: Path):
    (tmp_path / "projects.md").write_text(
        "# Realtime\nBuilt a FastAPI WebSocket ticker with persistent bidirectional communication.",
        encoding="utf-8",
    )
    matches = NotesTool(tmp_path).search("WebSocket persistent bidirectional", limit=2)
    assert matches
    assert "WebSocket" in matches[0].excerpt
    assert matches[0].source == "projects.md"


def test_search_is_read_only_and_ignores_progress_json(tmp_path: Path):
    (tmp_path / "notes.md").write_text("# Python\nUsed pytest for tests.", encoding="utf-8")
    (tmp_path / "progress.json").write_text('{"secret": "pytest"}', encoding="utf-8")
    matches = NotesTool(tmp_path).search("pytest")
    assert all(match.source != "progress.json" for match in matches)
