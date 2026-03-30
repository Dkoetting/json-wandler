from pathlib import Path
from app.core.models import GPTData


def convert_to_grok_instructions(gpt: GPTData, output_dir: Path, optimized_content: str | None = None) -> Path:
    if optimized_content:
        content = optimized_content
    else:
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
