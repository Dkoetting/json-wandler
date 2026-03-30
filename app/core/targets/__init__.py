from app.core.targets.claude import convert_to_claude_skill
from app.core.targets.gemini import convert_to_gemini_gem
from app.core.targets.grok import convert_to_grok_instructions
from app.core.targets.perplexity import convert_to_perplexity_instructions

TARGETS = {
    "claude": convert_to_claude_skill,
    "gemini": convert_to_gemini_gem,
    "grok": convert_to_grok_instructions,
    "perplexity": convert_to_perplexity_instructions,
}

ALL_TARGET_NAMES = list(TARGETS.keys())
