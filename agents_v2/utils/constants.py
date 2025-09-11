import enum
from typing import Any

from pydantic import BaseModel, Field

class ProviderType(str, enum.Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class RoleType(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class ToolCall(BaseModel):
    id: str = Field(
        ...,
        description="도구 호출 ID",
        examples=["tool_call_123"],
    )
    name: str = Field(
        ...,
        description="도구 이름",
        examples=["web_search", "calculator"],
    )
    arguments: dict[str, Any] = Field(
        ...,
        description="도구 호출에 사용되는 인수",
        examples=[{"query": "What is the capital of France?"}],
    )
    result: str = Field(
        ...,
        description="도구 호출 결과",
        examples=["The capital of France is Paris."],
    )