from pathlib import Path
from app.core.models import GPTData


def convert_to_gemini_gem(gpt: GPTData, output_dir: Path, optimized_content: str | None = None) -> Path:
    if optimized_content:
        content = optimized_content
    else:
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
