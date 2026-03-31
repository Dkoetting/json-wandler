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


def log_llm_call(
    source_name: str,
    target: str,
    provider: str,
    request_payload: dict,
    response_payload: dict,
    tokens_input: int = 0,
    tokens_output: int = 0,
    duration_ms: int = 0,
    error: str = "",
) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "type": "llm_call",
        "source_name": source_name,
        "target": target,
        "provider": provider,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "duration_ms": duration_ms,
        "error": error,
        "request": request_payload,
        "response": response_payload,
    }

    log_path = get_log_path()
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def read_logs(date: str | None = None) -> list[dict]:
    if date:
        log_path = LOG_DIR / f"migration-{date}.jsonl"
    else:
        log_path = get_log_path()

    if not log_path.exists():
        return []

    entries = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                entries.append(json.loads(line))
    return entries
