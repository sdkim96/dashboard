import enum

from typing import Any, Callable, Type
from pydantic import BaseModel, Field

import agents_v2.types as t

class ToolType(str, enum.Enum):
    web = "search"
    rag = "rag"


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
    output: Type[t.PydanticFormatType] = Field(
        ...,
        description="The output schema for the tool.",
    )


