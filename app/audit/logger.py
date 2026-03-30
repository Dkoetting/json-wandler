import json
import logging
from datetime import datetime, timezone
from pathlib import Path

LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)


def get_log_path() -> Path:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return LOG_DIR / f"migration-{today}.jsonl"


def log_migration(
    source_name: str,
    target: str,
    mode: str,
    status: str,
    output_path: str = "",
    error_message: str = "",
    tokens_input: int = 0,
    tokens_output: int = 0,
    duration_ms: int = 0,
    original_prompt: str = "",
    optimized_output: str = "",
    llm_request: dict | None = None,
    llm_response: dict | None = None,
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source_name": source_name,
        "target": target,
        "mode": mode,
        "status": status,
        "output_path": output_path,
        "error_message": error_message,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "duration_ms": duration_ms,
        "original_prompt": original_prompt,
        "optimized_output": optimized_output,
        "llm_request": llm_request,
        "llm_response": llm_response,
    }

    log_path = get_log_path()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    logging.getLogger("json_wandler").info(
        f"Migration: {source_name} -> {target} [{mode}] = {status}"
    )
