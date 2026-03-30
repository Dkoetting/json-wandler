import shutil
import tempfile
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.converter import convert_gpt
from app.core.parser import parse_gpt_file
from app.core.targets import ALL_TARGET_NAMES
from app.audit.logger import log_migration

load_dotenv()

app = FastAPI(title="JSON Wandler", description="ChatGPT GPT → Claude / Gemini / Grok / Perplexity Migrator")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

OUTPUT_DIR = Path(__file__).parent.parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "targets": ALL_TARGET_NAMES,
    })


@app.post("/migrate", response_class=HTMLResponse)
async def migrate(
    request: Request,
    json_file: UploadFile = File(...),
    targets: list[str] = Form(...),
    mode: str = Form("quick"),
):
    # Temporäre Datei anlegen und parsen
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        content = await json_file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)

    gpt = parse_gpt_file(tmp_path)
    tmp_path.unlink(missing_ok=True)

    if not gpt:
        return templates.TemplateResponse("result.html", {
            "request": request,
            "error": "Ungültige JSON-Datei. Bitte lade eine gültige GPT-JSON hoch.",
            "results": [],
        })

    results = convert_gpt(gpt, targets, mode, OUTPUT_DIR)

    # Loggen
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

    return templates.TemplateResponse("result.html", {
        "request": request,
        "error": None,
        "gpt_name": gpt.name,
        "results": results,
    })


@app.post("/migrate/batch", response_class=HTMLResponse)
async def migrate_batch(
    request: Request,
    json_files: list[UploadFile] = File(...),
    targets: list[str] = Form(...),
    mode: str = Form("quick"),
):
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

        results = convert_gpt(gpt, targets, mode, OUTPUT_DIR)
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

    return templates.TemplateResponse("result.html", {
        "request": request,
        "error": None if all_results else "Keine gültigen GPT-JSONs gefunden.",
        "gpt_name": f"{len(all_results)} Migrationen",
        "results": all_results,
    })


@app.get("/download/{filename}")
async def download(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        return HTMLResponse("Datei nicht gefunden.", status_code=404)
    return FileResponse(file_path, filename=filename)
