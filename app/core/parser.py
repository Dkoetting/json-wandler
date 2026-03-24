import json
import logging
from pathlib import Path
from typing import Optional

from app.core.models import GPTData

logger = logging.getLogger(__name__)


def parse_gpt_file(file_path: Path) -> Optional[GPTData]:
    try:
        raw = json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        return None

    try:
        return GPTData(**raw)
    except Exception as e:
        logger.error(f"Validation failed for {file_path}: {e}")
        return None


def parse_gpt_directory(dir_path: Path) -> list[GPTData]:
    results = []
    for file_path in sorted(dir_path.glob("*.json")):
        gpt = parse_gpt_file(file_path)
        if gpt is not None:
            results.append(gpt)
    return results
