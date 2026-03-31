from pathlib import Path
from app.core.models import GPTData


def convert_to_perplexity_instructions(gpt: GPTData, output_dir: Path, optimized_content: str | None = None) -> Path:
    if optimized_content:
        content = optimized_content
    else:
        content = f"""# {gpt.name} — Perplexity Space

## Recherche-Fokus
{gpt.description or gpt.name}

## Hauptaufgabe
{gpt.system_prompt or 'Recherchiere und beantworte Fragen zu diesem Themenbereich.'}

## Ausgabeformat
1. **Kurzzusammenfassung** (2-3 Sätze)
2. **Details** mit Quellenbelegen
3. **Quellen** (mindestens 2-3 verifizierte Quellen)

## Quellen-Anforderungen
- Bevorzuge aktuelle Quellen (< 2 Jahre)
- Wissenschaftliche Quellen bevorzugen wo verfügbar
- Immer Quellen zitieren

## Einschränkungen
- Nur faktisch belegte Informationen
- Bei Unsicherheit: klar kommunizieren"""

    out_path = output_dir / f"{gpt.slug}-perplexity-instructions.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path
