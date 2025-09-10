from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

from ..config import INPUT_DIR, DEFAULT_HOST, DEFAULT_PORT
from ..orchestrator.chain import run_latex_workflow
from ..storage.cache import get_record

app = FastAPI(title="Warp Engine")


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return """
    <html>
      <head><title>Warp Engine</title></head>
      <body>
        <h1>Warp Engine</h1>
        <ul>
          <li><a href="/latex">LaTeX workflow</a></li>
        </ul>
      </body>
    </html>
    """


@app.get("/latex", response_class=HTMLResponse)
async def latex_page() -> str:
    return """
    <html>
      <head><title>LaTeX Workflow</title></head>
      <body>
        <h2>LaTeX Workflow</h2>
        <form action="/api/run-latex" method="post" enctype="multipart/form-data">
          <div>
            <label>Paste LaTeX:</label><br/>
            <textarea name="latex" rows="18" cols="100" placeholder="Paste LaTeX here..."></textarea>
          </div>
          <div>
            <label>Or upload a file:</label>
            <input type="file" name="file" />
          </div>
          <div>
            <button type="submit">Run</button>
          </div>
        </form>
      </body>
    </html>
    """


@app.post("/api/run-latex")
async def api_run_latex(latex: Optional[str] = Form(None), file: Optional[UploadFile] = File(None)):
    latex_text = (latex or "").strip()
    file_path: Optional[Path] = None

    if file and file.filename:
        INPUT_DIR.mkdir(parents=True, exist_ok=True)
        dest = INPUT_DIR / file.filename
        data = await file.read()
        dest.write_bytes(data)
        file_path = dest
        if not latex_text:
            try:
                latex_text = data.decode("utf-8", errors="ignore")
            except Exception:
                latex_text = ""

    if not latex_text:
        return JSONResponse({"error": "No LaTeX provided (paste or upload a text file)."}, status_code=400)

    job_id, final_output = run_latex_workflow(latex_text)
    return {"id": job_id, "final": final_output}


@app.get("/api/jobs/{job_id}")
async def api_get_job(job_id: str):
    rec = get_record(job_id)
    if not rec:
        return JSONResponse({"error": "Not found"}, status_code=404)
    return rec


def run_server(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    uvicorn.run(app, host=host, port=port)

