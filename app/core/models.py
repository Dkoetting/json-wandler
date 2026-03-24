import re
from pydantic import BaseModel, field_validator


class GPTData(BaseModel):
    name: str
    url: str = ""
    id: str = ""
    description: str = ""
    system_prompt: str = ""
    conversation_starters: list[str] = []
    knowledge_files: list[str] = []
    recommended_model: str = ""
    capabilities: list[str] = []
    actions: list[str] = []

    @field_validator("name")
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("name must not be empty")
        return v.strip()

    @property
    def slug(self) -> str:
        return re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-")

    @property
    def has_content(self) -> bool:
        return bool(self.system_prompt.strip())


class MigrationResult(BaseModel):
    source_name: str
    target: str
    mode: str
    status: str  # "success", "error", "warning"
    output_path: str = ""
    error_message: str = ""
    tokens_input: int = 0
    tokens_output: int = 0
    duration_ms: int = 0
