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
    "claude": """Du bist ein Experte für Claude AI Skills und System Prompts.
Transformiere das folgende ChatGPT Custom GPT JSON in einen optimierten Claude Skill System Prompt.

CLAUDE SKILL ANFORDERUNGEN:
- Beginne mit einer klaren Rollendefinition in XML: <role>...</role>
- Nutze <instructions> für Hauptanweisungen
- Nutze <constraints> für Einschränkungen/Was der Skill NICHT tut
- Nutze <conversation_style> für Kommunikationsstil
- Nutze <examples> wenn Starter-Prompts vorhanden sind
- Entferne alle ChatGPT-spezifischen Referenzen (Plugins, DALL-E, ChatGPT-URLs)
- Aktiviere Reasoning wo sinnvoll ("Denke Schritt für Schritt")
- Behalte Mehrsprachigkeit wenn im Original definiert
- Gib NUR den fertigen System Prompt zurück, kein JSON

Original GPT: {name}
Beschreibung: {description}

System-Prompt:
{system_prompt}

Erstelle jetzt den optimierten Claude Skill Output:""",

    "gemini": """Du bist ein Experte für Google Gemini Gems.
Transformiere das folgende ChatGPT Custom GPT JSON in Gemini Gem Instruktionen.

GEMINI GEM ANFORDERUNGEN:
- Beginne mit: "# [Name] — Gemini Gem"
- Definiere eine klare Persona mit Namen und Charaktereigenschaften
- Sektion "## Hauptaufgabe" mit klaren Instruktionen
- Sektion "## Kommunikationsstil"
- Sektion "## Einschränkungen"
- Nutze Google-native Konzepte (Google Search, Google Workspace) wenn sinnvoll
- Beschreibe multimodale Fähigkeiten explizit wenn relevant
- Markdown-strukturiert für optimales Rendering
- Gib NUR die fertigen Gem-Instruktionen zurück

Original GPT: {name}
Beschreibung: {description}

System-Prompt:
{system_prompt}

Erstelle jetzt die optimierten Gem Instructions:""",

    "grok": """Du bist ein Experte für xAI Grok System Prompts.
Transformiere das folgende ChatGPT Custom GPT JSON in einen Grok System Prompt.

GROK ANFORDERUNGEN:
- Direkter, prägnanter Stil ohne Floskeln
- Beginne mit: "You are [Name], a specialized AI assistant."
- Kurze, klare Instruktionsblöcke
- Definiere explizit: Ton (ernst/humorvoll), Umfang, Grenzen
- Optional: Hinweis auf Realtime X/Twitter-Daten wenn relevant
- Keine langen verschachtelten Strukturen
- Englisch bevorzugt, außer Original ist klar deutsch
- Gib NUR den fertigen System Prompt zurück

Original GPT: {name}
Beschreibung: {description}

System-Prompt:
{system_prompt}

Erstelle jetzt den optimierten Grok System Prompt:""",

    "perplexity": """Du bist ein Experte für Perplexity AI Space Instructions.
Transformiere das folgende ChatGPT Custom GPT JSON in Perplexity Space Instructions.

PERPLEXITY ANFORDERUNGEN:
- Beginne mit klarer Beschreibung: was dieser Space recherchiert
- Definiere Quellen-Anforderungen explizit (Web/Academic/YouTube/Reddit)
- Sektion "Recherche-Fokus" mit Kernthemen
- Sektion "Ausgabeformat": Kurzzusammenfassung → Details → Quellen
- Definiere Sprache und Fachtiefe
- Betone Faktentreue über Kreativität
- Kein Fokus auf Konversation, sondern auf Informationsabruf
- Gib NUR die fertigen Space Instructions zurück

Original GPT: {name}
Beschreibung: {description}

System-Prompt:
{system_prompt}

Erstelle jetzt die optimierten Perplexity Space Instructions:""",
}


def optimize_for_target(gpt: GPTData, target: str, provider: str = "anthropic", api_key: str | None = None) -> OptimizationResult:
    """Optimize GPT content for target platform using LLM.

    Args:
        gpt: The parsed GPT data
        target: Target platform (claude, gemini, grok, perplexity)
        provider: LLM provider ("anthropic" or "openai")
        api_key: Optional API key override (from UI). Falls back to env var.
    """
    if provider == "openai":
        return _optimize_openai(gpt, target, api_key)
    else:
        return _optimize_anthropic(gpt, target, api_key)


def _optimize_anthropic(gpt: GPTData, target: str, api_key: str | None = None) -> OptimizationResult:
    key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
    if not key or key == "sk-ant-xxxxx":
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
        client = Anthropic(api_key=key)

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
        logger.error(f"Anthropic-Optimierung fehlgeschlagen: {e}")
        return OptimizationResult(error=str(e))


def _optimize_openai(gpt: GPTData, target: str, api_key: str | None = None) -> OptimizationResult:
    """Platzhalter für OpenAI-basierte Optimierung.

    Benötigt: pip install openai
    Wird aktiviert wenn OPENAI_API_KEY gesetzt oder Key über UI übergeben wird.
    """
    key = api_key or os.getenv("OPENAI_API_KEY", "")
    if not key:
        return OptimizationResult(error="Kein gültiger OPENAI_API_KEY gesetzt")

    if target not in TARGET_PROMPTS:
        return OptimizationResult(error=f"Unbekanntes Ziel: {target}")

    prompt = TARGET_PROMPTS[target].format(
        name=gpt.name,
        description=gpt.description,
        system_prompt=gpt.system_prompt[:12000],
    )

    try:
        import openai
        client = openai.OpenAI(api_key=key)

        request_payload = {
            "model": "gpt-4o",
            "messages": [
                {"role": "system", "content": "Du bist ein Experte für LLM Prompt Engineering und AI Platform Migration."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "max_tokens": 4096,
        }

        response = client.chat.completions.create(**request_payload)

        output_text = response.choices[0].message.content
        return OptimizationResult(
            output=output_text,
            tokens_input=response.usage.prompt_tokens,
            tokens_output=response.usage.completion_tokens,
            llm_request=request_payload,
            llm_response={"content": output_text, "model": response.model},
        )
    except ImportError:
        return OptimizationResult(error="OpenAI SDK nicht installiert. Bitte: pip install openai")
    except Exception as e:
        logger.error(f"OpenAI-Optimierung fehlgeschlagen: {e}")
        return OptimizationResult(error=str(e))
