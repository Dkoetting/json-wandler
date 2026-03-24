import json
import tempfile
from pathlib import Path
from app.core.parser import parse_gpt_file, parse_gpt_directory


def test_parse_valid_file(sample_gpt_json):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(sample_gpt_json, f)
        f.flush()
        result = parse_gpt_file(Path(f.name))
    assert result.name == "Academic Assistant"
    assert result.has_content is True


def test_parse_minimal_file(minimal_gpt_json):
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(minimal_gpt_json, f)
        f.flush()
        result = parse_gpt_file(Path(f.name))
    assert result.name == "Minimal Bot"


def test_parse_invalid_json():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write("not json{{{")
        f.flush()
        result = parse_gpt_file(Path(f.name))
    assert result is None


def test_parse_missing_name():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"system_prompt": "hello"}, f)
        f.flush()
        result = parse_gpt_file(Path(f.name))
    assert result is None


def test_parse_directory(sample_gpt_json, minimal_gpt_json):
    with tempfile.TemporaryDirectory() as tmpdir:
        for i, data in enumerate([sample_gpt_json, minimal_gpt_json]):
            path = Path(tmpdir) / f"gpt_{i}.json"
            path.write_text(json.dumps(data))
        results = parse_gpt_directory(Path(tmpdir))
    assert len(results) == 2


def test_parse_directory_skips_invalid(sample_gpt_json):
    with tempfile.TemporaryDirectory() as tmpdir:
        (Path(tmpdir) / "good.json").write_text(json.dumps(sample_gpt_json))
        (Path(tmpdir) / "bad.json").write_text("not json")
        results = parse_gpt_directory(Path(tmpdir))
    assert len(results) == 1
