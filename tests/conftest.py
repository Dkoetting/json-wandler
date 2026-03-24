import pytest


@pytest.fixture
def sample_gpt_json():
    return {
        "name": "Academic Assistant",
        "url": "https://chatgpt.com/g/g-5gkdnWsv4-academic-assistant",
        "id": "g-5gkdnWsv4",
        "description": "Helps with research papers",
        "system_prompt": "This GPT assists users in creating and refining scientific papers.",
        "conversation_starters": ["lets go :-)", "on"],
        "knowledge_files": [],
        "recommended_model": "",
        "capabilities": ["Web Search"],
        "actions": ["Thinking"],
    }


@pytest.fixture
def minimal_gpt_json():
    return {
        "name": "Minimal Bot",
        "system_prompt": "You are a helpful assistant.",
    }


@pytest.fixture
def invalid_gpt_json_no_name():
    return {
        "system_prompt": "You are a helpful assistant.",
    }


@pytest.fixture
def invalid_gpt_json_empty_prompt():
    return {
        "name": "Empty Bot",
        "system_prompt": "",
    }
