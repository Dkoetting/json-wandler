from pathlib import Path
from app.core.models import GPTData


def convert_to_gemini_gem(gpt: GPTData, output_dir: Path, optimized_content: str | None = None) -> Path:
    if optimized_content:
        content = optimized_content
    else:
        starters = [s for s in gpt.conversation_starters if s.lower() not in ("on",)]
        caps = gpt.capabilities

        starters_block = ""
        if starters:
            starters_block = f"""
## Beispiel-Eingaben
{chr(10).join(f'- "{s}"' for s in starters[:5])}"""

        google_search = "\n- Nutze Google Search für aktuelle Informationen" if "Web Search" in caps else ""

        content = f"""# {gpt.name} — Gemini Gem

## Persona
Du bist **{gpt.name}**{': ' + gpt.description if gpt.description else ''}.

## Hauptaufgabe
{gpt.system_prompt or 'Definiere hier die Hauptaufgabe.'}

## Kommunikationsstil
- Klar und strukturiert
- Nutze Markdown für Überschriften und Listen
- Stelle Rückfragen wenn Kontext fehlt

## Einschränkungen
- Bleibe im definierten Themenbereich{google_search}
{starters_block}
"""

    out_path = output_dir / f"{gpt.slug}-gemini-gem.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path
