import zipfile
import tempfile
from pathlib import Path
from app.core.models import GPTData
from app.core.targets.claude import convert_to_claude_skill
from app.core.targets.gemini import convert_to_gemini_gem
from app.core.targets.grok import convert_to_grok_instructions
from app.core.targets.perplexity import convert_to_perplexity_instructions


def _make_gpt():
    return GPTData(
        name="Academic Assistant",
        description="Helps with research papers",
        system_prompt="This GPT assists users in creating scientific papers.",
        conversation_starters=["lets go :-)"],
        capabilities=["Web Search"],
        knowledge_files=["paper_guide.pdf"],
    )


# --- Claude ---
def test_claude_skill_returns_zip():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_claude_skill(gpt, Path(tmpdir))
        assert result_path.suffix == ".zip"
        assert result_path.exists()


def test_claude_skill_zip_contains_skill_md():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_claude_skill(gpt, Path(tmpdir))
        with zipfile.ZipFile(result_path) as zf:
            assert "SKILL.md" in zf.namelist()


def test_claude_skill_content_has_frontmatter():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_claude_skill(gpt, Path(tmpdir))
        with zipfile.ZipFile(result_path) as zf:
            content = zf.read("SKILL.md").decode()
        assert content.startswith("---")
        assert "name: academic-assistant" in content
        assert "Academic Assistant" in content


def test_claude_skill_content_has_notes():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_claude_skill(gpt, Path(tmpdir))
        with zipfile.ZipFile(result_path) as zf:
            content = zf.read("SKILL.md").decode()
        assert "Web Search" in content
        assert "paper_guide.pdf" in content


# --- Gemini ---
def test_gemini_gem_creates_file():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_gemini_gem(gpt, Path(tmpdir))
        assert result_path.suffix == ".md"
        assert result_path.exists()


def test_gemini_gem_has_four_pillars():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_gemini_gem(gpt, Path(tmpdir))
        content = result_path.read_text()
    assert "Role (Pillar 1)" in content
    assert "Task (Pillar 2)" in content
    assert "Format (Pillar 3)" in content
    assert "Constraints (Pillar 4)" in content


# --- Grok ---
def test_grok_creates_file():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_grok_instructions(gpt, Path(tmpdir))
        assert result_path.suffix == ".md"
        assert result_path.exists()


def test_grok_has_instructions():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_grok_instructions(gpt, Path(tmpdir))
        content = result_path.read_text()
    assert "Instructions" in content
    assert gpt.system_prompt in content


# --- Perplexity ---
def test_perplexity_creates_file():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_perplexity_instructions(gpt, Path(tmpdir))
        assert result_path.suffix == ".md"
        assert result_path.exists()


def test_perplexity_has_focus_areas():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        result_path = convert_to_perplexity_instructions(gpt, Path(tmpdir))
        content = result_path.read_text()
    assert "Focus Areas" in content
