from pathlib import Path
from app.core.models import GPTData


def convert_to_grok_instructions(gpt: GPTData, output_dir: Path, optimized_content: str | None = None) -> Path:
    if optimized_content:
        content = optimized_content
    else:
        caps = gpt.capabilities
        realtime = "\n- Use real-time data when relevant" if "Web Search" in caps else ""

        content = f"""You are {gpt.name}, a specialized AI assistant.{' ' + gpt.description if gpt.description else ''}

## Core Instructions
{gpt.system_prompt or 'Define core behavior here.'}

## Behavior Rules
- Be direct and concise
- No unnecessary preambles{realtime}
- Stay within defined scope

## Tone
Professional, clear, efficient."""

    out_path = output_dir / f"{gpt.slug}-grok-instructions.md"
    out_path.write_text(content, encoding="utf-8")
    return out_path
