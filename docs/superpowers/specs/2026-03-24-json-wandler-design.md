# JSON Wandler — Design Spec

## Overview

CLI + Browser-based tool that migrates ChatGPT Custom GPT JSON exports to 4 target platforms: Claude Skill, Gemini Gem, Grok, and Perplexity. Supports a convenience "All at once" mode that runs all 4 targets in one pass. Two migration modes: 1:1 quick conversion and AI-optimized migration.

## Input Format

Custom GPT JSON files with this structure:
```json
{
  "name": "GPT Name",
  "url": "https://chatgpt.com/g/...",
  "id": "g-XXXXX",
  "description": "",
  "system_prompt": "...",
  "conversation_starters": [],
  "knowledge_files": [],
  "recommended_model": "",
  "capabilities": [],
  "actions": []
}
```

Source: `G:\OLD_GPT_Vault\gpts\` (10 GPTs currently)

### Field Handling

| Field | Handling |
|-------|----------|
| `name` | Used as output filename and title in all targets |
| `system_prompt` | Core content — converted/optimized for each target |
| `conversation_starters` | Mapped to trigger phrases (Claude), example prompts (Gemini), included as-is (Grok/Perplexity) |
| `description` | Used as summary/description in target output |
| `capabilities` | Noted in output as metadata (e.g., "Original GPT had: Web Search") |
| `knowledge_files` | Listed as reference — cannot be auto-migrated, user gets a note |
| `actions` | Listed as reference — noted as "manual setup required on target platform" |
| `url`, `id` | Logged for traceability, not used in output |
| `recommended_model` | Logged, not used |

### Validation

- **Required fields:** `name`, `system_prompt` (must be non-empty strings)
- **Optional fields:** all others (default to empty string/array)
- **Invalid JSON:** Error message with filename, skip file in batch mode
- **Empty system_prompt:** Warning, offer Quick Convert only (nothing to optimize)
- **Batch mode:** Errors on individual files don't stop the batch — each file gets its own status

## Target Platforms

1. **Claude Skill** — SKILL.md + ZIP
2. **Gemini Gem** — Four-Pillars structured Instructions
3. **Grok** — Custom Instructions for grok.com Settings
4. **Perplexity** — Custom Instructions for Perplexity Settings
5. **All at once** (convenience mode) — runs all 4 targets in one pass

## Output Formats (Quick Convert)

### Claude Skill
```markdown
---
name: academic-assistant
description: Migrated from ChatGPT: Academic Assistant
trigger_phrases:
  - "Academic Assistant"
  - "Helps in creating and refining research papers"
---

# Academic Assistant

## Role
[system_prompt content, restructured into sections]

## Conversation Starters
- "lets go :-)"

## Notes
- Original capabilities: Web Search
- Knowledge files: [none / list]
```
Output: `{name}-claude-skill.zip` containing `SKILL.md`

### Gemini Gem
```markdown
# Gemini Gem: Academic Assistant

## Role (Pillar 1)
[Who the Gem is]

## Task (Pillar 2)
[What it does — from system_prompt]

## Format (Pillar 3)
[How it responds]

## Constraints (Pillar 4)
[Rules and limitations]

## Example Prompts
- "lets go :-)"
```
Output: `{name}-gemini-gem.md`

### Grok Custom Instructions
```markdown
# Grok Custom Instructions: Academic Assistant

## Instructions
[system_prompt content, adapted for Grok's format]

## Conversation Starters
- "lets go :-)"
```
Output: `{name}-grok-instructions.md`

### Perplexity Custom Instructions
```markdown
# Perplexity Instructions: Academic Assistant

## Instructions
[system_prompt content, adapted for Perplexity's concise format]

## Focus Areas
[Extracted from capabilities and system_prompt]
```
Output: `{name}-perplexity-instructions.md`

## Migration Modes

- **Quick Convert (1:1):** Direct format transformation, no LLM calls. Maps fields to target format templates above.
- **AI-Optimized:** LLM analyzes system_prompt, restructures and optimizes for target platform best practices.

### AI-Optimization Strategy

**LLM used:** Claude (Anthropic SDK) for all targets. Single LLM for consistency and simplicity.

**Per-target optimization prompts:**
- **Claude Skill:** Restructure into Progressive Disclosure pattern, extract trigger phrases, add proper YAML frontmatter, create skill-creator-compliant structure
- **Gemini Gem:** Apply Four-Pillars framework (Role, Task, Format, Constraints), optimize for Gemini's instruction-following style
- **Grok:** Simplify and focus on direct instructions, match Grok's conversational style
- **Perplexity:** Condense to essential instructions, focus on search-augmented behavior

**LLM output validation:** Response must contain the expected markdown structure. If malformed, retry once, then fall back to Quick Convert with a warning in the log.

## Architecture

```
json_wandler_/
├── app/
│   ├── main.py              # FastAPI App + Routes
│   ├── cli.py               # CLI Interface (Click)
│   ├── core/
│   │   ├── parser.py        # GPT-JSON Parsing + Validation
│   │   ├── converter.py     # 1:1 Format Conversion
│   │   ├── optimizer.py     # LLM-based Optimization
│   │   └── targets/
│   │       ├── __init__.py
│   │       ├── claude.py    # -> Claude Skill (SKILL.md + ZIP)
│   │       ├── gemini.py    # -> Gemini Gem Instructions
│   │       ├── grok.py      # -> Grok Custom Instructions
│   │       └── perplexity.py # -> Perplexity Instructions
│   ├── templates/           # Jinja2 HTML (Web-UI)
│   │   ├── base.html
│   │   ├── index.html       # Start: target selection
│   │   ├── upload.html      # File upload (single/batch)
│   │   ├── options.html     # Quick Convert vs AI-Optimized
│   │   └── result.html      # Results + Downloads
│   ├── static/              # Tailwind CSS, HTMX
│   └── audit/
│       ├── logger.py        # Structured JSON logging
│       └── logs/            # Log files
├── output/                  # Generated migration results
├── tests/                   # pytest tests with real GPT fixtures
├── .env                     # API Keys (ANTHROPIC_API_KEY)
├── requirements.txt
└── README.md
```

## Tech Stack

- **Python 3.11+**
- **FastAPI** — API + serves HTML templates
- **Jinja2 + HTMX** — Dynamic browser UI without JS build step
- **Tailwind CSS** (via CDN) — Styling
- **Click** — CLI interface
- **Anthropic SDK** — Claude API for AI-optimization
- **python-dotenv** — .env loading
- **pytest** — Testing

## Web-UI Flow

1. **Start Screen** — Select target platform(s): Claude / Gemini / Grok / Perplexity / All
2. **Upload** — Drag & Drop or file picker. Single JSON or folder (batch). Shows preview: name, prompt length, capabilities.
3. **Options** — Choose mode: Quick Convert or AI-Optimized
4. **Processing** — Progress indicator per GPT
5. **Results** — Download buttons (individual + ZIP for batch), preview of converted output, "Convert another" button

## CLI Interface

```bash
# Single file, output to stdout + output/ directory
python -m app.cli migrate --input ./gpts/Academic_Assistant.json --target claude --mode optimized

# Batch (folder), all files written to output/
python -m app.cli migrate --input ./gpts/ --target all --mode quick

# List available targets
python -m app.cli targets
```

CLI writes converted files to `output/` directory and prints a summary table to stdout (filename, target, status, output path).

## Logging

JSON-structured log files in `app/audit/logs/`, one file per session:

```json
{
  "timestamp": "2026-03-24T14:30:00Z",
  "source_file": "Academic_Assistant_gkdnWsv4.json",
  "source_name": "Academic Assistant",
  "target": "claude",
  "mode": "optimized",
  "llm_used": "claude-sonnet-4-6",
  "tokens_input": 1250,
  "tokens_output": 890,
  "original_prompt": "...",
  "optimized_output": "...",
  "llm_request": { ... },
  "llm_response": { ... },
  "status": "success",
  "duration_ms": 3200
}
```

## Error Handling

- **API failure:** Retry once, then fall back to Quick Convert with warning
- **Rate limiting:** Sequential processing in batch mode (no parallel LLM calls)
- **Invalid input:** Skip with error in log + user message, continue batch
- **LLM malformed output:** Retry once, fall back to Quick Convert

## API Keys

- Phase A (local): `.env` file with `ANTHROPIC_API_KEY`
- Phase B (SaaS): UI input field, session-only storage, .env as fallback

## Phases

- **Phase A:** Local CLI + Browser UI, test with 10 GPTs from vault
- **Phase B:** Deploy as single service on Railway (server-rendered FastAPI), add auth + user key management
