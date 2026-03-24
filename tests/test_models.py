import pytest
from app.core.models import GPTData, MigrationResult


def test_gpt_data_full(sample_gpt_json):
    gpt = GPTData(**sample_gpt_json)
    assert gpt.name == "Academic Assistant"
    assert gpt.capabilities == ["Web Search"]
    assert gpt.slug == "academic-assistant"


def test_gpt_data_minimal(minimal_gpt_json):
    gpt = GPTData(**minimal_gpt_json)
    assert gpt.name == "Minimal Bot"
    assert gpt.capabilities == []
    assert gpt.knowledge_files == []


def test_gpt_data_missing_name(invalid_gpt_json_no_name):
    with pytest.raises(Exception):
        GPTData(**invalid_gpt_json_no_name)


def test_gpt_data_empty_prompt(invalid_gpt_json_empty_prompt):
    gpt = GPTData(**invalid_gpt_json_empty_prompt)
    assert gpt.has_content is False


def test_migration_result():
    result = MigrationResult(
        source_name="Test",
        target="claude",
        mode="quick",
        status="success",
        output_path="output/test-claude-skill.zip",
    )
    assert result.status == "success"
