import json
from pathlib import Path

from fastapi.testclient import TestClient

from warpengine.server.ui import app


def test_run_latex_endpoint(monkeypatch, tmp_path: Path):
    # Monkeypatch the workflow to avoid external API calls
    from warpengine.server import ui as ui_module

    def fake_run_latex_workflow(text: str):
        return ("job-test-123", "Final text")

    monkeypatch.setattr(ui_module, "run_latex_workflow", fake_run_latex_workflow)

    client = TestClient(app)
    resp = client.post("/api/run-latex", data={"latex": "\\section{Intro} Hello."})
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] == "job-test-123"
    assert body["final"] == "Final text"
