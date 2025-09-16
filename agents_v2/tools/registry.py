from typing import Any
from pydantic import Field
from openai import AsyncOpenAI

import agents_v2.types as t

from agents_v2.tools.spec import ToolSpec, ToolType
from agents_v2.tools.manager import ToolManager
from agents_v2.providers.openai import OpenAIProvider

ai_provider = OpenAIProvider(client=AsyncOpenAI())

class WeatherQuery(t.PydanticFormatType):
    location: str = Field(..., description="Location to get the weather for")

    @classmethod
    def default(cls) -> "WeatherQuery":
        return WeatherQuery(location="seoul")

class WeatherResponse(t.PydanticFormatType):
    report: str = Field(..., description="Weather report for the queried location")

    @classmethod
    def default(cls) -> "WeatherResponse":
        return WeatherResponse(report="The weather is sunny for the location: seoul")

async def weather_report(params: WeatherQuery) -> WeatherResponse:
    return WeatherResponse(report=f"The weather is sunny for the location: {params.location}")

class Registry(dict):

    def __init__(self) -> None:
        super().__init__()

    def get_manager(self, tool_name: str) -> ToolManager:
        item = self.get(tool_name)
        if item is None:
            raise ValueError(f"Tool '{tool_name}' not found in registry")
        return item["manager"]
    
    def get_function(self, tool_name: str) -> Any:
        item = self.get(tool_name)
        if item is None:
            raise ValueError(f"Tool '{tool_name}' not found in registry")
        return item["function"]
    
    def get_output_schema(self, tool_name: str) -> type[t.PydanticFormatType]:
        item = self.get(tool_name)
        if item is None:
            raise ValueError(f"Tool '{tool_name}' not found in registry")
        return item["output_schema"]

REGISTRY = Registry()
REGISTRY["weather"] = {
    "manager": ToolManager(
        ai=ai_provider,
        toolspec=ToolSpec(
            name="WeatherQuery",
            type=ToolType.search,
            description="A tool to query the weather.",
            parameters=WeatherQuery
        )
    ),
    "function": weather_report,
    "output_schema": WeatherResponse,
}
