import os
import logging
from dataclasses import dataclass, field

from app.core.models import GPTData

logger = logging.getLogger(__name__)


@dataclass
class OptimizationResult:
    output: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    llm_request: dict = field(default_factory=dict)
    llm_response: dict = field(default_factory=dict)
    error: str = ""


TARGET_PROMPTS = {
    "claude": """Du bist ein Experte für Claude Skills (SKILL.md Format).
Wandle den folgenden ChatGPT System-Prompt in einen optimierten Claude Skill um.

Regeln:
- Beginne mit YAML-Frontmatter (name, description, trigger_phrases)
- Nutze Progressive Disclosure: Kernverhalten zuerst, Details danach
- Strukturiere mit klaren Markdown-Überschriften
- Entferne ChatGPT-spezifische Referenzen
- Behalte die Kernlogik und das Fachwissen bei

Original GPT: {name}
Beschreibung: {description}

System-Prompt:
{system_prompt}

Erstelle jetzt den optimierten SKILL.md Inhalt:""",

    "gemini": """Du bist ein Experte für Google Gemini Gems.
Wandle den folgenden ChatGPT System-Prompt in optimierte Gemini Gem Instructions um.

Nutze die Four-Pillars-Struktur:
1. Role (Pillar 1): Wer ist das Gem?
2. Task (Pillar 2): Was soll es tun?
3. Format (Pillar 3): Wie soll die Ausgabe aussehen?
4. Constraints (Pillar 4): Was sind die Grenzen?

Original GPT: {name}
Beschreibung: {description}

System-Prompt:
{system_prompt}

Erstelle jetzt die optimierten Gem Instructions:""",

    "grok": """Du bist ein Experte für Grok Custom Instructions (grok.com).
Wandle den folgenden ChatGPT System-Prompt in optimierte Grok Custom Instructions um.

Regeln:
- Kompakt und direkt (Grok bevorzugt prägnante Anweisungen)
- Entferne ChatGPT-spezifische Referenzen
- Behalte die Kernlogik bei
- Fokus auf Verhaltensanweisungen

Original GPT: {name}
Beschreibung: {description}

System-Prompt:
{system_prompt}

Erstelle jetzt die optimierten Grok Custom Instructions:""",

    "perplexity": """Du bist ein Experte für Perplexity AI Instructions.
Wandle den folgenden ChatGPT System-Prompt in optimierte Perplexity Instructions um.

Regeln:
- Fokus auf Recherche-Anweisungen (Perplexity ist eine Suchmaschine)
- Quellennutzung und Faktencheck betonen
- Entferne ChatGPT-spezifische Referenzen
- Kompakt halten

Original GPT: {name}
Beschreibung: {description}

System-Prompt:
{system_prompt}

Erstelle jetzt die optimierten Perplexity Instructions:""",
}


def optimize_for_target(gpt: GPTData, target: str) -> OptimizationResult:
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "sk-ant-xxxxx":
        return OptimizationResult(error="Kein gültiger ANTHROPIC_API_KEY gesetzt")

    if target not in TARGET_PROMPTS:
        return OptimizationResult(error=f"Unbekanntes Ziel: {target}")

    prompt = TARGET_PROMPTS[target].format(
        name=gpt.name,
        description=gpt.description,
        system_prompt=gpt.system_prompt[:12000],
    )

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)

        request_payload = {
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }

        response = client.messages.create(**request_payload)

        output_text = response.content[0].text
        return OptimizationResult(
            output=output_text,
            tokens_input=response.usage.input_tokens,
            tokens_output=response.usage.output_tokens,
            llm_request=request_payload,
            llm_response={"content": output_text, "model": response.model},
        )
    except Exception as e:
        logger.error(f"LLM-Optimierung fehlgeschlagen: {e}")
        return OptimizationResult(error=str(e))
