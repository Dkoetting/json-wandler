import zipfile
from pathlib import Path
from app.core.models import GPTData


def convert_to_claude_skill(gpt: GPTData, output_dir: Path, optimized_content: str | None = None) -> Path:
    if optimized_content:
        skill_md = optimized_content
    else:
        starters = gpt.conversation_starters
        starters_filtered = [s for s in starters if s.lower() not in ("on",)]
        starters_yaml = "\n".join(f'  - "{s}"' for s in starters_filtered)
        starters_list = "\n".join(f"- {s}" for s in starters_filtered)
        caps = gpt.capabilities

        examples_block = ""
        if starters_filtered:
            examples_block = f"""
<examples>
Beispiel-Einstiege:
{starters_list}
</examples>"""

        web_search_line = "\n- Nutze Web-Suche für aktuelle Informationen" if "Web Search" in caps else ""

        skill_md = f"""---
name: {gpt.slug}
description: "Migrated from ChatGPT: {gpt.name}"
trigger_phrases:
{starters_yaml}
---

<role>
Du bist {gpt.name}, ein spezialisierter KI-Assistent.
{gpt.description}
</role>

<instructions>
{gpt.system_prompt or 'Keine spezifischen Instruktionen definiert.'}
</instructions>

<constraints>
- Bleibe immer im definierten Aufgabenbereich
- Verweise bei Bedarf auf verfügbare Optionen{web_search_line}
</constraints>

<conversation_style>
- Strukturiert und klar
- Frage bei Unklarheiten nach
</conversation_style>
{examples_block}

## Notes
- Original capabilities: {', '.join(caps) if caps else 'none'}
- Knowledge files: {', '.join(gpt.knowledge_files) if gpt.knowledge_files else 'none'}
- Actions: {', '.join(gpt.actions) if gpt.actions else 'none'}
"""

    zip_path = output_dir / f"{gpt.slug}-claude-skill.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("SKILL.md", skill_md)
    return zip_path
