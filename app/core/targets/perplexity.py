from pathlib import Path
from app.core.models import GPTData


def convert_to_perplexity_instructions(gpt: GPTData, output_dir: Path, optimized_content: str | None = None) -> Path:
    if optimized_content:
        content = optimized_content
    else:
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
