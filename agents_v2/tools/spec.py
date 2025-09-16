import enum

from typing import Type, Generic, Any
from pydantic import BaseModel, Field, ConfigDict

import agents_v2.types as t


class ToolType(str, enum.Enum):
    web = "web"
    rag = "rag"
    calculator = "calculator"
    search = "search"


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


class ToolSpec(BaseModel):
    name: str = Field(
        ...,
        description="The name of the tool.",
        examples=["search_web", "rag_tool"]
    )
    type: ToolType = Field(
        ...,
        description="The type of the tool.",
        examples=[ToolType.web, ToolType.rag]
    )
    description: str = Field(
        ...,
        description="A brief description of the tool's functionality.",
        examples=["Search the web for information.", "Perform calculations."]
    )
    parameters: Type[t.PydanticFormatType] = Field(
        ...,
        description="The parameters schema for the tool.",
    )


class ToolResponse(BaseModel, Generic[t.ToolOutputT]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    output: t.ToolOutputT | None = Field(
        ...,
        description="The output of the tool.",
    )
    error: Exception | None = Field(
        None,
        description="An error that occurred during tool execution, if any.",
    )   
    tool_name: str = Field(
        ...,
        description="The name of the tool that was called.",
    )
    tool_arguments: dict | None = Field(
        None,
        description="The arguments used for the tool call.",
    )


