import zipfile
from pathlib import Path

from app.core.models import GPTData


def convert_to_claude_skill(gpt: GPTData, output_dir: Path, optimized_content: str | None = None) -> Path:
    if optimized_content:
        skill_md = optimized_content
    else:
        starters_yaml = "\n".join(f'  - "{s}"' for s in gpt.conversation_starters if s.lower() not in ("on",))
        starters_list = "\n".join(f'- "{s}"' for s in gpt.conversation_starters if s.lower() not in ("on",))

        capabilities_note = ", ".join(gpt.capabilities) if gpt.capabilities else "none"
        knowledge_note = ", ".join(gpt.knowledge_files) if gpt.knowledge_files else "none"
        actions_note = ", ".join(gpt.actions) if gpt.actions else "none"

        skill_md = f"""---
name: {gpt.slug}
description: "Migrated from ChatGPT: {gpt.name}"
trigger_phrases:
{starters_yaml}
---

# {gpt.name}

## Role
{gpt.system_prompt}

## Conversation Starters
{starters_list}

## Notes
- Original capabilities: {capabilities_note}
- Knowledge files: {knowledge_note}
- Actions: {actions_note}
"""

    zip_path = output_dir / f"{gpt.slug}-claude-skill.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("SKILL.md", skill_md)
    return zip_path
