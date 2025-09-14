import enum

from typing import Type, TypeVar, Generic
from pydantic import BaseModel, Field, ConfigDict

import agents_v2.types as t



class ToolType(str, enum.Enum):
    web = "web"
    rag = "rag"
    calculator = "calculator"


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


