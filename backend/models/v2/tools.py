from typing import List

from pydantic import BaseModel, Field

class ToolRequest(BaseModel):
    name: str = Field(
        ...,
        description="도구 이름",
        examples=["web_search", "calculator"],
    )
    type : str = Field(
        ...,
        description="도구 유형",
        examples=["search", "rag"],
    )