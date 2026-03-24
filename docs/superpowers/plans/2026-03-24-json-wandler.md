# JSON Wandler Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a CLI + Browser tool that migrates ChatGPT Custom GPT JSONs to Claude Skill, Gemini Gem, Grok, and Perplexity formats with Quick Convert and AI-Optimized modes.

**Architecture:** Python FastAPI app serving both a CLI (Click) and a browser UI (Jinja2 + HTMX). Core logic in `app/core/` handles parsing, conversion, and LLM optimization. Each target platform has its own module under `app/core/targets/`. Structured JSON logging in `app/audit/`.

**Tech Stack:** Python 3.11+, FastAPI, Jinja2, HTMX, Tailwind CSS (CDN), Click, Anthropic SDK, python-dotenv, pytest

**Spec:** `docs/superpowers/specs/2026-03-24-json-wandler-design.md`

---

## File Structure

| File | Responsibility |
|------|---------------|
| `app/__init__.py` | Package init |
| `app/main.py` | FastAPI app, routes, file upload handling |
| `app/cli.py` | Click CLI: migrate command, targets command |
| `app/core/__init__.py` | Package init |
| `app/core/models.py` | Pydantic models for GPT data and migration results |
| `app/core/parser.py` | Load + validate GPT JSON files |
| `app/core/converter.py` | Orchestrator: route to target + mode |
| `app/core/optimizer.py` | LLM calls via Anthropic SDK |
| `app/core/targets/__init__.py` | Target registry |
| `app/core/targets/claude.py` | Claude Skill output (SKILL.md + ZIP) |
| `app/core/targets/gemini.py` | Gemini Gem output |
| `app/core/targets/grok.py` | Grok Custom Instructions output |
| `app/core/targets/perplexity.py` | Perplexity Instructions output |
| `app/audit/__init__.py` | Package init |
| `app/audit/logger.py` | Structured JSON logger |
| `app/audit/logs/` | Log output directory |
| `app/templates/base.html` | Base HTML template (Tailwind + HTMX) |
| `app/templates/index.html` | Start screen: target selection + file upload + mode selection (single-page form — deliberate simplification of spec's multi-step wizard) |
| `app/templates/result.html` | Results + downloads |
| `app/static/style.css` | Custom CSS (minimal, Tailwind handles most) |
| `output/` | Generated files land here |
| `tests/conftest.py` | Shared fixtures (sample GPT JSON data) |
| `tests/test_parser.py` | Parser tests |
| `tests/test_targets.py` | Target conversion tests |
| `tests/test_converter.py` | Orchestrator tests |
| `tests/test_cli.py` | CLI integration tests |
| `requirements.txt` | Dependencies |
| `.env.example` | Template for API keys |

---

## Chunk 1: Project Setup + Parser

### Task 1: Project scaffolding

**Files:**
- Create: `requirements.txt`
- Create: `.env.example`
- Create: `app/__init__.py`
- Create: `app/core/__init__.py`
- Create: `app/core/targets/__init__.py`
- Create: `app/audit/__init__.py`
- Create: `output/.gitkeep`
- Create: `app/audit/logs/.gitkeep`

- [ ] **Step 1: Create requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
jinja2==3.1.4
python-multipart==0.0.9
python-dotenv==1.0.1
click==8.1.7
anthropic==0.40.0
pydantic==2.9.0
pytest==8.3.3
httpx==0.27.0
```

- [ ] **Step 2: Create .env.example**

```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

- [ ] **Step 3: Create all __init__.py files and directories**

```python
# app/__init__.py — empty
# app/core/__init__.py — empty
# app/core/targets/__init__.py — empty
# app/audit/__init__.py — empty
```

Also create `output/.gitkeep` and `app/audit/logs/.gitkeep` (empty files).

- [ ] **Step 4: Create virtual environment and install dependencies**

Run: `cd D:/json_wandler_ && python -m venv venv && venv/Scripts/pip install -r requirements.txt`
Expected: All packages install successfully.

- [ ] **Step 5: Initialize git repo and commit**

```bash
cd D:/json_wandler_
git init
echo "venv/" > .gitignore
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "app/audit/logs/*.json" >> .gitignore
echo "output/*" >> .gitignore
echo "!output/.gitkeep" >> .gitignore
echo "!app/audit/logs/.gitkeep" >> .gitignore
git add -A
git commit -m "chore: initial project scaffolding"
```

---

### Task 2: Pydantic models

**Files:**
- Create: `app/core/models.py`
- Create: `tests/conftest.py`

- [ ] **Step 1: Write test fixtures**

```python
# tests/conftest.py
import pytest

@pytest.fixture
def sample_gpt_json():
    return {
        "name": "Academic Assistant",
        "url": "https://chatgpt.com/g/g-5gkdnWsv4-academic-assistant",
        "id": "g-5gkdnWsv4",
        "description": "Helps with research papers",
        "system_prompt": "This GPT assists users in creating and refining scientific papers.",
        "conversation_starters": ["lets go :-)", "on"],
        "knowledge_files": [],
        "recommended_model": "",
        "capabilities": ["Web Search"],
        "actions": ["Thinking"]
    }

@pytest.fixture
def minimal_gpt_json():
    return {
        "name": "Minimal Bot",
        "system_prompt": "You are a helpful assistant."
    }

@pytest.fixture
def invalid_gpt_json_no_name():
    return {
        "system_prompt": "You are a helpful assistant."
    }

@pytest.fixture
def invalid_gpt_json_empty_prompt():
    return {
        "name": "Empty Bot",
        "system_prompt": ""
    }
```

- [ ] **Step 2: Write model tests**

```python
# tests/test_models.py
from app.core.models import GPTData, MigrationResult

def test_gpt_data_full(sample_gpt_json):
    gpt = GPTData(**sample_gpt_json)
    assert gpt.name == "Academic Assistant"
    assert gpt.capabilities == ["Web Search"]
    assert gpt.slug == "academic-assistant"

def test_gpt_data_minimal(minimal_gpt_json):
    gpt = GPTData(**minimal_gpt_json)
    assert gpt.name == "Minimal Bot"
    assert gpt.capabilities == []
    assert gpt.knowledge_files == []

def test_gpt_data_missing_name(invalid_gpt_json_no_name):
    import pytest
    with pytest.raises(Exception):
        GPTData(**invalid_gpt_json_no_name)

def test_gpt_data_empty_prompt(invalid_gpt_json_empty_prompt):
    gpt = GPTData(**invalid_gpt_json_empty_prompt)
    assert gpt.has_content is False

def test_migration_result():
    result = MigrationResult(
        source_name="Test",
        target="claude",
        mode="quick",
        status="success",
        output_path="output/test-claude-skill.zip"
    )
    assert result.status == "success"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_models.py -v`
Expected: FAIL — `app.core.models` does not exist yet.

- [ ] **Step 4: Implement models**

```python
# app/core/models.py
import re
from pydantic import BaseModel, field_validator
from typing import Optional


class GPTData(BaseModel):
    name: str
    url: str = ""
    id: str = ""
    description: str = ""
    system_prompt: str = ""
    conversation_starters: list[str] = []
    knowledge_files: list[str] = []
    recommended_model: str = ""
    capabilities: list[str] = []
    actions: list[str] = []

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @property
    def slug(self) -> str:
        return re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-")

    @property
    def has_content(self) -> bool:
        return bool(self.system_prompt.strip())


class MigrationResult(BaseModel):
    source_name: str
    target: str
    mode: str
    status: str  # "success", "error", "warning"
    output_path: str = ""
    error_message: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    duration_ms: int = 0
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_models.py -v`
Expected: All 5 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add app/core/models.py tests/conftest.py tests/test_models.py
git commit -m "feat: add GPTData and MigrationResult pydantic models"
```

---

### Task 3: JSON Parser

**Files:**
- Create: `app/core/parser.py`
- Create: `tests/test_parser.py`

- [ ] **Step 1: Write parser tests**

```python
# tests/test_parser.py
import json
import tempfile
from pathlib import Path
from app.core.parser import parse_gpt_file, parse_gpt_directory

def test_parse_valid_file(sample_gpt_json):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_gpt_json, f)
        f.flush()
        result = parse_gpt_file(Path(f.name))
    assert result.name == "Academic Assistant"
    assert result.has_content is True

def test_parse_minimal_file(minimal_gpt_json):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(minimal_gpt_json, f)
        f.flush()
        result = parse_gpt_file(Path(f.name))
    assert result.name == "Minimal Bot"

def test_parse_invalid_json():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("not json{{{")
        f.flush()
        result = parse_gpt_file(Path(f.name))
    assert result is None

def test_parse_missing_name():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"system_prompt": "hello"}, f)
        f.flush()
        result = parse_gpt_file(Path(f.name))
    assert result is None

def test_parse_directory(sample_gpt_json, minimal_gpt_json):
    with tempfile.TemporaryDirectory() as tmpdir:
        for i, data in enumerate([sample_gpt_json, minimal_gpt_json]):
            path = Path(tmpdir) / f"gpt_{i}.json"
            path.write_text(json.dumps(data))
        results = parse_gpt_directory(Path(tmpdir))
    assert len(results) == 2

def test_parse_directory_skips_invalid(sample_gpt_json):
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "good.json").write_text(json.dumps(sample_gpt_json))
        (Path(tmpdir) / "bad.json").write_text("not json")
        results = parse_gpt_directory(Path(tmpdir))
    assert len(results) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_parser.py -v`
Expected: FAIL — `app.core.parser` does not exist yet.

- [ ] **Step 3: Implement parser**

```python
# app/core/parser.py
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
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_parser.py -v`
Expected: All 6 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/core/parser.py tests/test_parser.py
git commit -m "feat: add GPT JSON parser with validation"
```

---

## Chunk 2: Target Converters (Quick Convert)

### Task 4: Claude Skill target

**Files:**
- Create: `app/core/targets/claude.py`
- Create: `tests/test_targets.py`

- [ ] **Step 1: Write Claude target tests**

```python
# tests/test_targets.py
import zipfile
import tempfile
from pathlib import Path
from app.core.models import GPTData
from app.core.targets.claude import convert_to_claude_skill


def _make_gpt():
    return GPTData(
        name="Academic Assistant",
        description="Helps with research papers",
        system_prompt="This GPT assists users in creating scientific papers.",
        conversation_starters=["lets go :-)"],
        capabilities=["Web Search"],
        knowledge_files=["paper_guide.pdf"],
    )


def test_claude_skill_returns_zip():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_claude_skill(gpt, Path(tmpdir))
        assert result_path.suffix == ".zip"
        assert result_path.exists()


def test_claude_skill_zip_contains_skill_md():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_claude_skill(gpt, Path(tmpdir))
        with zipfile.ZipFile(result_path) as zf:
            assert "SKILL.md" in zf.namelist()


def test_claude_skill_content_has_frontmatter():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_claude_skill(gpt, Path(tmpdir))
        with zipfile.ZipFile(result_path) as zf:
            content = zf.read("SKILL.md").decode()
        assert content.startswith("---")
        assert "name: academic-assistant" in content
        assert "Academic Assistant" in content


def test_claude_skill_content_has_notes():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_claude_skill(gpt, Path(tmpdir))
        with zipfile.ZipFile(result_path) as zf:
            content = zf.read("SKILL.md").decode()
        assert "Web Search" in content
        assert "paper_guide.pdf" in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_targets.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement Claude target**

```python
# app/core/targets/claude.py
import zipfile
from pathlib import Path

from app.core.models import GPTData


def convert_to_claude_skill(gpt: GPTData, output_dir: Path) -> Path:
    starters = "\n".join(f'  - "{s}"' for s in gpt.conversation_starters if s.lower() not in ("on",))

    capabilities_note = ", ".join(gpt.capabilities) if gpt.capabilities else "none"
    knowledge_note = ", ".join(gpt.knowledge_files) if gpt.knowledge_files else "none"

    skill_md = f"""---
name: {gpt.slug}
description: "Migrated from ChatGPT: {gpt.name}"
trigger_phrases:
{starters}
---

# {gpt.name}

## Role
{gpt.system_prompt}

## Conversation Starters
{chr(10).join(f'- "{s}"' for s in gpt.conversation_starters if s.lower() not in ("on",))}

## Notes
- Original capabilities: {capabilities_note}
- Knowledge files: {knowledge_note}
- Actions: {", ".join(gpt.actions) if gpt.actions else "none"}
"""

    zip_path = output_dir / f"{gpt.slug}-claude-skill.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("SKILL.md", skill_md)
    return zip_path
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_targets.py -v`
Expected: All 4 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/core/targets/claude.py tests/test_targets.py
git commit -m "feat: add Claude Skill target converter"
```

---

### Task 5: Gemini, Grok, and Perplexity targets

**Files:**
- Create: `app/core/targets/gemini.py`
- Create: `app/core/targets/grok.py`
- Create: `app/core/targets/perplexity.py`
- Modify: `tests/test_targets.py`

- [ ] **Step 1: Add tests for all 3 targets**

Append to `tests/test_targets.py`:

```python
from app.core.targets.gemini import convert_to_gemini_gem
from app.core.targets.grok import convert_to_grok_instructions
from app.core.targets.perplexity import convert_to_perplexity_instructions


# --- Gemini ---
def test_gemini_gem_creates_file():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_gemini_gem(gpt, Path(tmpdir))
        assert result_path.suffix == ".md"
        assert result_path.exists()

def test_gemini_gem_has_four_pillars():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_gemini_gem(gpt, Path(tmpdir))
        content = result_path.read_text()
    assert "Role (Pillar 1)" in content
    assert "Task (Pillar 2)" in content
    assert "Format (Pillar 3)" in content
    assert "Constraints (Pillar 4)" in content

# --- Grok ---
def test_grok_creates_file():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_grok_instructions(gpt, Path(tmpdir))
        assert result_path.suffix == ".md"
        assert result_path.exists()

def test_grok_has_instructions():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_grok_instructions(gpt, Path(tmpdir))
        content = result_path.read_text()
    assert "Instructions" in content
    assert gpt.system_prompt in content

# --- Perplexity ---
def test_perplexity_creates_file():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_perplexity_instructions(gpt, Path(tmpdir))
        assert result_path.suffix == ".md"
        assert result_path.exists()

def test_perplexity_has_focus_areas():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_perplexity_instructions(gpt, Path(tmpdir))
        content = result_path.read_text()
    assert "Focus Areas" in content
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_targets.py -v`
Expected: FAIL — modules don't exist yet.

- [ ] **Step 3: Implement Gemini target**

```python
# app/core/targets/gemini.py
from pathlib import Path
from app.core.models import GPTData


def convert_to_gemini_gem(gpt: GPTData, output_dir: Path) -> Path:
    starters = "\n".join(f"- {s}" for s in gpt.conversation_starters if s.lower() not in ("on",))

    content = f"""# Gemini Gem: {gpt.name}

## Role (Pillar 1)
{gpt.description or gpt.name}

## Task (Pillar 2)
{gpt.system_prompt}

## Format (Pillar 3)
Respond clearly and structured. Use markdown formatting where appropriate.

## Constraints (Pillar 4)
Follow the instructions above precisely. Stay in character.

## Example Prompts
{starters}
"""
    out_path = output_dir / f"{gpt.slug}-gemini-gem.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path
```

- [ ] **Step 4: Implement Grok target**

```python
# app/core/targets/grok.py
from pathlib import Path
from app.core.models import GPTData


def convert_to_grok_instructions(gpt: GPTData, output_dir: Path) -> Path:
    starters = "\n".join(f"- {s}" for s in gpt.conversation_starters if s.lower() not in ("on",))

    content = f"""# Grok Custom Instructions: {gpt.name}

## Instructions
{gpt.system_prompt}

## Conversation Starters
{starters}
"""
    out_path = output_dir / f"{gpt.slug}-grok-instructions.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path
```

- [ ] **Step 5: Implement Perplexity target**

```python
# app/core/targets/perplexity.py
from pathlib import Path
from app.core.models import GPTData


def convert_to_perplexity_instructions(gpt: GPTData, output_dir: Path) -> Path:
    capabilities = ", ".join(gpt.capabilities) if gpt.capabilities else "General assistance"

    content = f"""# Perplexity Instructions: {gpt.name}

## Instructions
{gpt.system_prompt}

## Focus Areas
{capabilities}
"""
    out_path = output_dir / f"{gpt.slug}-perplexity-instructions.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path
```

- [ ] **Step 6: Run tests to verify they pass**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_targets.py -v`
Expected: All 10 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add app/core/targets/gemini.py app/core/targets/grok.py app/core/targets/perplexity.py tests/test_targets.py
git commit -m "feat: add Gemini, Grok, and Perplexity target converters"
```

---

### Task 6: Target registry + Converter orchestrator

**Files:**
- Modify: `app/core/targets/__init__.py`
- Create: `app/core/converter.py`
- Create: `tests/test_converter.py`

- [ ] **Step 1: Implement target registry**

```python
# app/core/targets/__init__.py
from app.core.targets.claude import convert_to_claude_skill
from app.core.targets.gemini import convert_to_gemini_gem
from app.core.targets.grok import convert_to_grok_instructions
from app.core.targets.perplexity import convert_to_perplexity_instructions

TARGETS = {
    "claude": convert_to_claude_skill,
    "gemini": convert_to_gemini_gem,
    "grok": convert_to_grok_instructions,
    "perplexity": convert_to_perplexity_instructions,
}

ALL_TARGET_NAMES = list(TARGETS.keys())
```

- [ ] **Step 2: Write converter tests**

```python
# tests/test_converter.py
import tempfile
from pathlib import Path
from app.core.models import GPTData
from app.core.converter import convert_gpt


def _make_gpt():
    return GPTData(
        name="Test Bot",
        system_prompt="You are a test bot.",
        conversation_starters=["hello"],
    )


def test_convert_single_target():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        results = convert_gpt(gpt, targets=["claude"], mode="quick", output_dir=Path(tmpdir))
    assert len(results) == 1
    assert results[0].status == "success"
    assert results[0].target == "claude"


def test_convert_all_targets():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        results = convert_gpt(gpt, targets=["all"], mode="quick", output_dir=Path(tmpdir))
    assert len(results) == 4


def test_convert_unknown_target():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        results = convert_gpt(gpt, targets=["unknown"], mode="quick", output_dir=Path(tmpdir))
    assert len(results) == 1
    assert results[0].status == "error"
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_converter.py -v`
Expected: FAIL.

- [ ] **Step 4: Implement converter**

```python
# app/core/converter.py
import time
from pathlib import Path

from app.core.models import GPTData, MigrationResult
from app.core.targets import TARGETS, ALL_TARGET_NAMES


def convert_gpt(
    gpt: GPTData,
    targets: list[str],
    mode: str,
    output_dir: Path,
) -> list[MigrationResult]:
    if "all" in targets:
        targets = ALL_TARGET_NAMES

    results = []
    for target_name in targets:
        start = time.time()

        if target_name not in TARGETS:
            results.append(MigrationResult(
                source_name=gpt.name,
                target=target_name,
                mode=mode,
                status="error",
                error_message=f"Unknown target: {target_name}",
            ))
            continue

        try:
            convert_fn = TARGETS[target_name]
            output_path = convert_fn(gpt, output_dir)
            duration = int((time.time() - start) * 1000)

            results.append(MigrationResult(
                source_name=gpt.name,
                target=target_name,
                mode=mode,
                status="success",
                output_path=str(output_path),
                duration_ms=duration,
            ))
        except Exception as e:
            results.append(MigrationResult(
                source_name=gpt.name,
                target=target_name,
                mode=mode,
                status="error",
                error_message=str(e),
            ))

    return results
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_converter.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 6: Commit**

```bash
git add app/core/targets/__init__.py app/core/converter.py tests/test_converter.py
git commit -m "feat: add target registry and converter orchestrator"
```

---

## Chunk 3: Audit Logger + CLI

### Task 7: Structured JSON logger

**Files:**
- Create: `app/audit/logger.py`
- Create: `tests/test_logger.py`

Note: Spec shows single JSON objects per session. We use JSONL (JSON Lines) instead — one JSON object per line, appended. This is better for streaming/append-only logging and easier to parse line-by-line.

- [ ] **Step 1: Write logger tests**

```python
# tests/test_logger.py
import json
import tempfile
from pathlib import Path
from app.audit.logger import AuditLogger
from app.core.models import MigrationResult


def test_logger_creates_log_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=Path(tmpdir))
        result = MigrationResult(
            source_name="Test",
            target="claude",
            mode="quick",
            status="success",
            output_path="output/test.zip",
        )
        logger.log(result, original_prompt="hello", optimized_output="world")
        log_files = list(Path(tmpdir).glob("*.jsonl"))
        assert len(log_files) == 1


def test_logger_writes_valid_jsonl():
    with tempfile.TemporaryDirectory() as tmpdir:
        logger = AuditLogger(log_dir=Path(tmpdir))
        result = MigrationResult(
            source_name="Test",
            target="gemini",
            mode="optimized",
            status="success",
        )
        logger.log(result, original_prompt="test prompt")
        log_file = list(Path(tmpdir).glob("*.jsonl"))[0]
        line = log_file.read_text().strip().split("\n")[0]
        entry = json.loads(line)
        assert entry["source_name"] == "Test"
        assert entry["target"] == "gemini"
        assert "timestamp" in entry
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_logger.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement logger**

```python
# app/audit/logger.py
import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.models import MigrationResult


class AuditLogger:
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"session_{timestamp}.jsonl"

    def log(
        self,
        result: MigrationResult,
        original_prompt: str = "",
        optimized_output: str = "",
        llm_request: dict | None = None,
        llm_response: dict | None = None,
    ):
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_name": result.source_name,
            "target": result.target,
            "mode": result.mode,
            "status": result.status,
            "output_path": result.output_path,
            "error_message": result.error_message,
            "tokens_input": result.tokens_input,
            "tokens_output": result.tokens_output,
            "duration_ms": result.duration_ms,
            "original_prompt": original_prompt,
            "optimized_output": optimized_output,
            "llm_request": llm_request,
            "llm_response": llm_response,
        }
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_logger.py -v`
Expected: All 2 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/audit/logger.py tests/test_logger.py
git commit -m "feat: add structured JSON audit logger"
```

---

### Task 8: CLI interface

**Files:**
- Create: `app/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write CLI tests**

```python
# tests/test_cli.py
import json
import tempfile
from pathlib import Path
from click.testing import CliRunner
from app.cli import cli


def _create_test_gpt(tmpdir: str) -> Path:
    data = {
        "name": "CLI Test Bot",
        "system_prompt": "You help with CLI testing.",
        "conversation_starters": ["test"],
    }
    path = Path(tmpdir) / "test_bot.json"
    path.write_text(json.dumps(data))
    return path


def test_cli_targets_command():
    runner = CliRunner()
    result = runner.invoke(cli, ["targets"])
    assert result.exit_code == 0
    assert "claude" in result.output
    assert "gemini" in result.output


def test_cli_migrate_single_file():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        gpt_path = _create_test_gpt(tmpdir)
        output_dir = Path(tmpdir) / "out"
        output_dir.mkdir()
        result = runner.invoke(cli, [
            "migrate",
            "--input", str(gpt_path),
            "--target", "claude",
            "--mode", "quick",
            "--output", str(output_dir),
        ])
        assert result.exit_code == 0
        assert "success" in result.output.lower()


def test_cli_migrate_batch():
    runner = CliRunner()
    with tempfile.TemporaryDirectory() as tmpdir:
        _create_test_gpt(tmpdir)
        output_dir = Path(tmpdir) / "out"
        output_dir.mkdir()
        result = runner.invoke(cli, [
            "migrate",
            "--input", tmpdir,
            "--target", "all",
            "--mode", "quick",
            "--output", str(output_dir),
        ])
        assert result.exit_code == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_cli.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement CLI**

```python
# app/cli.py
from pathlib import Path

import click

from app.core.converter import convert_gpt
from app.core.parser import parse_gpt_file, parse_gpt_directory
from app.core.targets import ALL_TARGET_NAMES
from app.audit.logger import AuditLogger


@click.group()
def cli():
    """JSON Wandler — Migrate ChatGPT Custom GPTs to other platforms."""
    pass


@cli.command()
def targets():
    """List available target platforms."""
    click.echo("Available targets:")
    for name in ALL_TARGET_NAMES:
        click.echo(f"  - {name}")
    click.echo(f"  - all (runs all {len(ALL_TARGET_NAMES)} targets)")


@cli.command()
@click.option("--input", "input_path", required=True, type=click.Path(exists=True), help="JSON file or directory")
@click.option("--target", required=True, help="Target platform: claude, gemini, grok, perplexity, all")
@click.option("--mode", default="quick", type=click.Choice(["quick", "optimized"]), help="Migration mode")
@click.option("--output", "output_dir", default="output", type=click.Path(), help="Output directory")
def migrate(input_path: str, target: str, mode: str, output_dir: str):
    """Migrate GPT JSON(s) to target platform(s)."""
    input_p = Path(input_path)
    output_p = Path(output_dir)
    output_p.mkdir(parents=True, exist_ok=True)

    log_dir = Path("app/audit/logs")
    audit = AuditLogger(log_dir=log_dir)

    # Parse input
    if input_p.is_file():
        gpt = parse_gpt_file(input_p)
        if gpt is None:
            click.echo(f"ERROR: Could not parse {input_p}", err=True)
            raise SystemExit(1)
        gpts = [gpt]
    else:
        gpts = parse_gpt_directory(input_p)
        if not gpts:
            click.echo(f"ERROR: No valid GPT JSONs found in {input_p}", err=True)
            raise SystemExit(1)

    click.echo(f"Found {len(gpts)} GPT(s). Migrating to '{target}' in '{mode}' mode...\n")

    target_list = [target]
    all_results = []

    for gpt in gpts:
        if not gpt.has_content:
            click.echo(f"  [WARN] {gpt.name}: empty system_prompt — only Quick Convert available")
            if mode == "optimized":
                mode = "quick"
        results = convert_gpt(gpt, targets=target_list, mode=mode, output_dir=output_p)
        for r in results:
            audit.log(r, original_prompt=gpt.system_prompt)
            status_icon = "OK" if r.status == "success" else "FAIL"
            click.echo(f"  [{status_icon}] {gpt.name} -> {r.target}: {r.output_path or r.error_message}")
        all_results.extend(results)

    success = sum(1 for r in all_results if r.status == "success")
    click.echo(f"\nDone: {success}/{len(all_results)} successful.")


if __name__ == "__main__":
    cli()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_cli.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/cli.py tests/test_cli.py
git commit -m "feat: add Click CLI with migrate and targets commands"
```

---

## Chunk 4: Web UI (FastAPI + Jinja2 + HTMX)

### Task 9: FastAPI app + base template

**Files:**
- Create: `app/main.py`
- Create: `app/templates/base.html`
- Create: `app/templates/index.html`
- Create: `app/static/style.css`

- [ ] **Step 1: Implement FastAPI app with index route**

```python
# app/main.py
from pathlib import Path

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.parser import parse_gpt_file
from app.core.converter import convert_gpt
from app.core.targets import ALL_TARGET_NAMES
from app.audit.logger import AuditLogger

import json
import tempfile

app = FastAPI(title="JSON Wandler")

BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

audit = AuditLogger(log_dir=BASE_DIR / "audit" / "logs")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "targets": ALL_TARGET_NAMES,
    })


@app.post("/upload", response_class=HTMLResponse)
async def upload(
    request: Request,
    target: str = Form(...),
    mode: str = Form("quick"),
    files: list[UploadFile] = File(...),
):
    results = []
    for upload_file in files:
        content = await upload_file.read()
        try:
            raw = json.loads(content)
        except json.JSONDecodeError:
            results.append({"name": upload_file.filename, "status": "error", "message": "Invalid JSON"})
            continue

        from app.core.models import GPTData
        try:
            gpt = GPTData(**raw)
        except Exception as e:
            results.append({"name": upload_file.filename, "status": "error", "message": str(e)})
            continue

        migration_results = convert_gpt(gpt, targets=[target], mode=mode, output_dir=OUTPUT_DIR)
        for r in migration_results:
            audit.log(r, original_prompt=gpt.system_prompt)
            results.append({
                "name": gpt.name,
                "target": r.target,
                "status": r.status,
                "output_path": r.output_path,
                "error": r.error_message,
            })

    return templates.TemplateResponse("result.html", {
        "request": request,
        "results": results,
    })


@app.get("/download/{filename}")
async def download(filename: str):
    file_path = (OUTPUT_DIR / filename).resolve()
    if not file_path.is_relative_to(OUTPUT_DIR.resolve()) or not file_path.exists():
        return HTMLResponse("File not found", status_code=404)
    return FileResponse(file_path, filename=filename)
```

- [ ] **Step 2: Create base template**

```html
<!-- app/templates/base.html -->
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JSON Wandler — {% block title %}Home{% endblock %}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/htmx.org@2.0.0"></script>
    <link rel="stylesheet" href="/static/style.css">
</head>
<body class="bg-gray-950 text-gray-100 min-h-screen">
    <div class="max-w-4xl mx-auto px-4 py-8">
        <header class="mb-8">
            <h1 class="text-3xl font-bold text-white">
                <a href="/">JSON Wandler</a>
            </h1>
            <p class="text-gray-400 mt-1">Migrate ChatGPT Custom GPTs to Claude, Gemini, Grok & Perplexity</p>
        </header>
        <main>
            {% block content %}{% endblock %}
        </main>
        <footer class="mt-12 pt-4 border-t border-gray-800 text-gray-500 text-sm">
            JSON Wandler v0.1 — Phase A (Local)
        </footer>
    </div>
</body>
</html>
```

- [ ] **Step 3: Create index template**

```html
<!-- app/templates/index.html -->
{% extends "base.html" %}
{% block title %}Start{% endblock %}
{% block content %}
<form action="/upload" method="post" enctype="multipart/form-data" class="space-y-8">

    <section>
        <h2 class="text-xl font-semibold mb-4">1. Zielplattform waehlen</h2>
        <div class="grid grid-cols-2 gap-3">
            {% for t in targets %}
            <label class="flex items-center gap-3 p-3 bg-gray-900 rounded-lg border border-gray-700 hover:border-blue-500 cursor-pointer">
                <input type="radio" name="target" value="{{ t }}" class="accent-blue-500" {% if loop.first %}checked{% endif %}>
                <span class="capitalize">{{ t }}</span>
            </label>
            {% endfor %}
            <label class="flex items-center gap-3 p-3 bg-gray-900 rounded-lg border border-gray-700 hover:border-blue-500 cursor-pointer">
                <input type="radio" name="target" value="all" class="accent-blue-500">
                <span>Alle auf einmal</span>
            </label>
        </div>
    </section>

    <section>
        <h2 class="text-xl font-semibold mb-4">2. JSON hochladen</h2>
        <div class="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center hover:border-blue-500 transition-colors">
            <input type="file" name="files" accept=".json" multiple class="block w-full text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:bg-blue-600 file:text-white hover:file:bg-blue-700">
            <p class="mt-2 text-gray-400 text-sm">Einzelne .json Datei oder mehrere auswaehlen (Batch)</p>
        </div>
    </section>

    <section>
        <h2 class="text-xl font-semibold mb-4">3. Modus waehlen</h2>
        <div class="flex gap-4">
            <label class="flex-1 p-4 bg-gray-900 rounded-lg border border-gray-700 hover:border-blue-500 cursor-pointer">
                <input type="radio" name="mode" value="quick" checked class="accent-blue-500">
                <span class="ml-2 font-medium">Quick Convert (1:1)</span>
                <p class="text-gray-400 text-sm mt-1">Direkte Format-Konvertierung, kein LLM</p>
            </label>
            <label class="flex-1 p-4 bg-gray-900 rounded-lg border border-gray-700 hover:border-blue-500 cursor-pointer">
                <input type="radio" name="mode" value="optimized" class="accent-blue-500">
                <span class="ml-2 font-medium">AI-Optimized</span>
                <p class="text-gray-400 text-sm mt-1">LLM optimiert fuer Zielplattform</p>
            </label>
        </div>
    </section>

    <button type="submit" class="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors">
        Migration starten
    </button>
</form>
{% endblock %}
```

- [ ] **Step 4: Create result template**

```html
<!-- app/templates/result.html -->
{% extends "base.html" %}
{% block title %}Ergebnis{% endblock %}
{% block content %}
<h2 class="text-xl font-semibold mb-6">Migration abgeschlossen</h2>

<div class="space-y-3">
{% for r in results %}
    <div class="p-4 rounded-lg {% if r.status == 'success' %}bg-green-900/30 border border-green-700{% else %}bg-red-900/30 border border-red-700{% endif %}">
        <div class="flex items-center justify-between">
            <div>
                <span class="font-medium">{{ r.name }}</span>
                {% if r.target %}
                <span class="text-gray-400 ml-2">-> {{ r.target }}</span>
                {% endif %}
                <span class="ml-2 px-2 py-0.5 rounded text-xs {% if r.status == 'success' %}bg-green-700{% else %}bg-red-700{% endif %}">
                    {{ r.status }}
                </span>
            </div>
            {% if r.status == 'success' and r.output_path %}
            <a href="/download/{{ r.output_path.split('/')[-1] }}"
               class="px-4 py-1 bg-blue-600 hover:bg-blue-700 rounded text-sm transition-colors">
                Download
            </a>
            {% endif %}
        </div>
        {% if r.error %}
        <p class="text-red-400 text-sm mt-2">{{ r.error }}</p>
        {% endif %}
    </div>
{% endfor %}
</div>

<div class="mt-8 flex gap-4">
    <a href="/" class="px-6 py-2 bg-gray-700 hover:bg-gray-600 rounded-lg transition-colors">
        Neue Migration starten
    </a>
</div>
{% endblock %}
```

- [ ] **Step 5: Create minimal CSS**

```css
/* app/static/style.css */
/* Custom overrides — Tailwind handles most styling via CDN */
body {
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}
```

- [ ] **Step 6: Manual test — start server and verify in browser**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m uvicorn app.main:app --reload --port 8000`

Open http://localhost:8000 in browser. Verify:
1. Index page shows target selection, file upload, mode selection
2. Upload a GPT JSON, select "claude", "quick" -> get result page with download link
3. Download link works

- [ ] **Step 7: Commit**

```bash
git add app/main.py app/templates/ app/static/
git commit -m "feat: add web UI with FastAPI, Jinja2, HTMX, Tailwind"
```

---

## Chunk 5: AI-Optimized Mode

### Task 10: LLM optimizer

**Files:**
- Create: `app/core/optimizer.py`
- Create: `tests/test_optimizer.py`

- [ ] **Step 1: Write optimizer tests (mocked LLM)**

```python
# tests/test_optimizer.py
from unittest.mock import patch, MagicMock
from app.core.optimizer import optimize_for_target
from app.core.models import GPTData


def _make_gpt():
    return GPTData(
        name="Test Bot",
        system_prompt="You are a helpful test bot that answers questions.",
        conversation_starters=["hello"],
        capabilities=["Web Search"],
    )


def _mock_claude_response(content: str):
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text=content)]
    mock_response.usage.input_tokens = 100
    mock_response.usage.output_tokens = 200
    return mock_response


@patch("app.core.optimizer.get_client")
def test_optimize_for_claude(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.messages.create.return_value = _mock_claude_response("---\nname: test-bot\n---\n# Test Bot\nOptimized content")

    gpt = _make_gpt()
    result = optimize_for_target(gpt, "claude")
    assert result.output is not None
    assert "test-bot" in result.output.lower() or "Test Bot" in result.output


@patch("app.core.optimizer.get_client")
def test_optimize_returns_tokens(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.messages.create.return_value = _mock_claude_response("optimized content")

    gpt = _make_gpt()
    result = optimize_for_target(gpt, "gemini")
    assert result.tokens_input == 100
    assert result.tokens_output == 200


@patch("app.core.optimizer.get_client")
def test_optimize_retries_then_fails(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_client.messages.create.side_effect = Exception("API down")

    gpt = _make_gpt()
    result = optimize_for_target(gpt, "claude")
    assert result.output is None
    assert result.error is not None
    assert mock_client.messages.create.call_count == 2  # retried once
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_optimizer.py -v`
Expected: FAIL.

- [ ] **Step 3: Implement optimizer**

```python
# app/core/optimizer.py
import os
from dataclasses import dataclass

from dotenv import load_dotenv

from app.core.models import GPTData

load_dotenv()

OPTIMIZATION_PROMPTS = {
    "claude": """You are an expert at creating Claude Skills. Convert this ChatGPT Custom GPT into a Claude Skill.

Requirements:
- YAML frontmatter with: name (slug), description, trigger_phrases
- Progressive Disclosure structure
- Clear sections: Role, Instructions, Conversation Starters, Notes
- Preserve all original functionality

Input GPT:
Name: {name}
Description: {description}
System Prompt:
{system_prompt}

Conversation Starters: {starters}
Capabilities: {capabilities}

Output the complete SKILL.md content (including --- frontmatter ---).""",

    "gemini": """You are an expert at creating Gemini Gems. Convert this ChatGPT Custom GPT into Gemini Gem Instructions using the Four-Pillars framework.

Requirements:
- Pillar 1 (Role): Who the Gem is
- Pillar 2 (Task): What it does
- Pillar 3 (Format): How it responds
- Pillar 4 (Constraints): Rules and limitations
- Example Prompts section
- Optimize for Gemini's instruction-following style

Input GPT:
Name: {name}
Description: {description}
System Prompt:
{system_prompt}

Conversation Starters: {starters}

Output the complete Gemini Gem instructions in markdown.""",

    "grok": """You are an expert at writing Grok Custom Instructions. Convert this ChatGPT Custom GPT into Grok-optimized Custom Instructions.

Requirements:
- Direct, conversational instruction style
- Keep it concise — Grok works best with focused instructions
- Include conversation starters
- Preserve core functionality

Input GPT:
Name: {name}
Description: {description}
System Prompt:
{system_prompt}

Conversation Starters: {starters}

Output the complete Grok Custom Instructions in markdown.""",

    "perplexity": """You are an expert at writing Perplexity Custom Instructions. Convert this ChatGPT Custom GPT into Perplexity-optimized Instructions.

Requirements:
- Concise and search-augmented focus
- Emphasize research and source quality
- Focus Areas section based on capabilities
- Preserve core functionality

Input GPT:
Name: {name}
Description: {description}
System Prompt:
{system_prompt}

Capabilities: {capabilities}

Output the complete Perplexity Instructions in markdown.""",
}


@dataclass
class OptimizationResult:
    output: str | None
    tokens_input: int = 0
    tokens_output: int = 0
    error: str | None = None
    llm_request: dict | None = None
    llm_response: dict | None = None


def get_client():
    from anthropic import Anthropic
    return Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def optimize_for_target(gpt: GPTData, target: str) -> OptimizationResult:
    prompt_template = OPTIMIZATION_PROMPTS.get(target)
    if not prompt_template:
        return OptimizationResult(output=None, error=f"No optimization prompt for target: {target}")

    user_prompt = prompt_template.format(
        name=gpt.name,
        description=gpt.description or gpt.name,
        system_prompt=gpt.system_prompt,
        starters=", ".join(gpt.conversation_starters),
        capabilities=", ".join(gpt.capabilities) if gpt.capabilities else "none",
    )

    request_body = {
        "model": "claude-sonnet-4-6-20250514",
        "max_tokens": 4096,
        "messages": [{"role": "user", "content": user_prompt}],
    }

    client = get_client()
    last_error = None

    for attempt in range(2):  # retry once on failure
        try:
            response = client.messages.create(**request_body)
            output_text = response.content[0].text

            return OptimizationResult(
                output=output_text,
                tokens_input=response.usage.input_tokens,
                tokens_output=response.usage.output_tokens,
                llm_request=request_body,
                llm_response={"content": output_text},
            )
        except Exception as e:
            last_error = str(e)

    return OptimizationResult(output=None, error=f"Failed after 2 attempts: {last_error}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/json_wandler_ && venv/Scripts/python -m pytest tests/test_optimizer.py -v`
Expected: All 3 tests PASS.

- [ ] **Step 5: Commit**

```bash
git add app/core/optimizer.py tests/test_optimizer.py
git commit -m "feat: add LLM optimizer with per-target prompts"
```

---

### Task 11: Wire optimizer into converter + CLI + web

**Files:**
- Modify: `app/core/converter.py` (add optimized mode)
- Modify: `app/core/targets/claude.py` (accept pre-optimized content)
- Modify: `app/core/targets/gemini.py` (accept pre-optimized content)
- Modify: `app/core/targets/grok.py` (accept pre-optimized content)
- Modify: `app/core/targets/perplexity.py` (accept pre-optimized content)

- [ ] **Step 1: Update all target converters to accept optional `optimized_content` parameter**

Each target function gets a new signature: `def convert_to_X(gpt: GPTData, output_dir: Path, optimized_content: str | None = None) -> Path`

When `optimized_content` is provided, use it instead of the template-based conversion.

For Claude: write `optimized_content` directly as SKILL.md.
For others: write `optimized_content` directly as the .md file.

- [ ] **Step 2: Update converter to call optimizer when mode is "optimized"**

Add to `convert_gpt()`: if `mode == "optimized"`, call `optimize_for_target(gpt, target_name)` first, then pass result to the target converter. Log the optimization result. If optimization fails, fall back to quick convert with a warning.

- [ ] **Step 3: Update target registry to pass optimized_content through**

```python
# In app/core/converter.py, updated convert_gpt function:
from app.core.optimizer import optimize_for_target

# Inside the loop:
optimized_content = None
opt_result = None
if mode == "optimized" and gpt.has_content:
    opt_result = optimize_for_target(gpt, target_name)
    if opt_result.output:
        optimized_content = opt_result.output

output_path = convert_fn(gpt, output_dir, optimized_content=optimized_content)
```

- [ ] **Step 4: Test manually with real API key**

```bash
cd D:/json_wandler_
# Add your real key to .env first
echo "ANTHROPIC_API_KEY=sk-ant-your-key" > .env
venv/Scripts/python -m app.cli migrate --input "G:/OLD_GPT_Vault/gpts/Academic_Assistant_gkdnWsv4.json" --target claude --mode optimized --output output
```

- [ ] **Step 5: Commit**

```bash
git add app/core/converter.py app/core/targets/
git commit -m "feat: wire AI-optimized mode through converter and targets"
```

---

## Chunk 6: Integration Test with Real Data

### Task 12: Full integration test

- [ ] **Step 1: Run CLI against all 10 GPTs, Quick Convert, all targets**

```bash
cd D:/json_wandler_
venv/Scripts/python -m app.cli migrate --input "G:/OLD_GPT_Vault/gpts/" --target all --mode quick --output output
```

Verify: 40 output files (10 GPTs x 4 targets), all status "success".

- [ ] **Step 2: Run CLI against one GPT, AI-Optimized, all targets**

```bash
venv/Scripts/python -m app.cli migrate --input "G:/OLD_GPT_Vault/gpts/Academic_Assistant_gkdnWsv4.json" --target all --mode optimized --output output
```

Verify: 4 output files, check quality of optimized content.

- [ ] **Step 3: Test web UI in browser**

```bash
cd D:/json_wandler_ && venv/Scripts/python -m uvicorn app.main:app --reload --port 8000
```

Upload Academic_Assistant JSON via browser, test both modes, download results.

- [ ] **Step 4: Check logs**

Verify `app/audit/logs/` contains JSONL files with complete entries.

- [ ] **Step 5: Run full test suite**

```bash
cd D:/json_wandler_ && venv/Scripts/python -m pytest -v
```

All tests should pass.

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "feat: JSON Wandler MVP complete — CLI + Web UI + Quick Convert + AI-Optimized"
```
