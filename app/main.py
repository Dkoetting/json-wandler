import json
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.converter import convert_gpt
from app.core.models import GPTData
from app.core.parser import parse_gpt_file
from app.core.targets import ALL_TARGET_NAMES
from app.audit.logger import log_migration

load_dotenv()

app = FastAPI(title="JSON Wandler", description="ChatGPT GPT → Claude / Gemini / Grok / Perplexity Migrator")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = BASE_DIR / "templates" / "index.html"
    return HTMLResponse(html_path.read_text(encoding="utf-8"))


@app.get("/api/targets")
async def get_targets():
    return {"targets": ALL_TARGET_NAMES}


@app.post("/api/migrate")
async def api_migrate(
    json_file: UploadFile = File(...),
    target: str = Form("all"),
    mode: str = Form("quick"),
    provider: str = Form("anthropic"),
):
    """API-Endpunkt für einzelne Migration (vom Frontend aufgerufen)."""
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        content = await json_file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    gpt = parse_gpt_file(tmp_path)
    tmp_path.unlink(missing_ok=True)

    if not gpt:
        return JSONResponse(
            status_code=400,
            content={"error": "Ungültige JSON-Datei. Bitte eine gültige GPT-JSON hochladen."},
        )

    targets = [target] if target != "all" else ["all"]
    results = convert_gpt(gpt, targets, mode, OUTPUT_DIR, provider=provider)

    for r in results:
        log_migration(
            source_name=r.source_name,
            target=r.target,
            mode=r.mode,
            status=r.status,
            output_path=r.output_path,
            error_message=r.error_message,
            tokens_input=r.tokens_input,
            tokens_output=r.tokens_output,
            duration_ms=r.duration_ms,
            original_prompt=gpt.system_prompt[:500],
        )

    return {
        "gpt_name": gpt.name,
        "results": [r.model_dump() for r in results],
    }


@app.post("/api/migrate/batch")
async def api_migrate_batch(
    json_files: list[UploadFile] = File(...),
    target: str = Form("all"),
    mode: str = Form("quick"),
    provider: str = Form("anthropic"),
):
    """Batch-Migration mehrerer GPT-JSONs."""
    all_results = []

    for json_file in json_files:
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
            content = await json_file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)

        gpt = parse_gpt_file(tmp_path)
        tmp_path.unlink(missing_ok=True)

        if not gpt:
            continue

        targets = [target] if target != "all" else ["all"]
        results = convert_gpt(gpt, targets, mode, OUTPUT_DIR, provider=provider)

        for r in results:
            log_migration(
                source_name=r.source_name,
                target=r.target,
                mode=r.mode,
                status=r.status,
                output_path=r.output_path,
                error_message=r.error_message,
                tokens_input=r.tokens_input,
                tokens_output=r.tokens_output,
                duration_ms=r.duration_ms,
                original_prompt=gpt.system_prompt[:500] if gpt else "",
            )
        all_results.extend(results)

    return {
        "total": len(all_results),
        "results": [r.model_dump() for r in all_results],
    }


@app.get("/download/{filename}")
async def download(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        return HTMLResponse("Datei nicht gefunden.", status_code=404)
    return FileResponse(file_path, filename=filename)
