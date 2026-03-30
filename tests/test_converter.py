import tempfile
from pathlib import Path
from app.core.models import GPTData
from app.core.converter import convert_gpt


def _make_gpt():
    return GPTData(
        name="Test Bot",
        system_prompt="You are a test bot.",
        conversation_starters=["hello"],
    )


def test_convert_single_target():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        results = convert_gpt(gpt, targets=["claude"], mode="quick", output_dir=Path(tmpdir))
    assert len(results) == 1
    assert results[0].status == "success"
    assert results[0].target == "claude"


def test_convert_all_targets():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        results = convert_gpt(gpt, targets=["all"], mode="quick", output_dir=Path(tmpdir))
    assert len(results) == 4


def test_convert_unknown_target():
    gpt = _make_gpt()
    with tempfile.TemporaryDirectory() as tmpdir:
        results = convert_gpt(gpt, targets=["unknown"], mode="quick", output_dir=Path(tmpdir))
    assert len(results) == 1
    assert results[0].status == "error"
