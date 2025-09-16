from enum import Enum
from typing import Awaitable, Callable, Type, Tuple, cast
from inspect import iscoroutinefunction, getattr_static

import agents_v2.types as t

from agents_v2.providers.base import BaseProvider
from agents_v2.providers.openai import ModelEnum
from agents_v2.tools.spec import ToolSpec, ToolResponse, ToolCall
from agents_v2.memory.history import History, HistoryItem, RoleType


class ToolManager:
    
    def __init__(
        self,
        *,
        ai: BaseProvider,
        toolspec: ToolSpec,
    ):
        self.ai = ai
        self.toolspec = toolspec

        if error := self._inspect_fn():
            raise error
       

    @property
    def toolparam_prompt(self) -> Tuple[str, str]:
        return (
"""
## 역할
당신은 매우 유능한 AI 도구 매개변수 생성기입니다.

## 목적
당신의 목적은 주어진 도구 설명과 도구 이름을 기반으로 도구 매개변수를 생성하는 것입니다.

## 도구 설명

{name}:
{description}

""",
"""
도구 매개변수를 생성해주세요.
"""
        )
    
    @property
    def chosen_model(self) -> Enum:
        if self.ai.provider_name == "openai":
            model = ModelEnum.gpt_4o_mini
        else:
            raise ValueError(f"Unsupported provider: {self.ai.provider_name}")
        return model
    
    def _inspect_fn(self) -> Exception | None:
        try:
            params_type = self.toolspec.parameters
        except Exception as e:
            return TypeError(f"Invalid toolspec.parameters: {e}")

        if not isinstance(params_type, type) or not issubclass(params_type, t.PydanticFormatType):
            return TypeError("toolspec.parameters must be a subclass of t.PydanticFormatType")

        try:
            sub_attr = getattr_static(params_type, "default")
            base_attr = getattr_static(t.PydanticFormatType, "default")
        except Exception:
            return AttributeError("toolspec.parameters must define classmethod default()")

        def _unwrap(x):
            return x.__func__ if isinstance(x, classmethod) else x

        if _unwrap(sub_attr) is _unwrap(base_attr):
            return NotImplementedError(
                "toolspec.parameters.default() must be implemented and not inherited from t.PydanticFormatType"
            )
        try:
            default_callable = getattr(params_type, "default")
            if not callable(default_callable):
                return TypeError("toolspec.parameters.default must be callable")
            default_instance = default_callable()
            if not isinstance(default_instance, params_type):
                return TypeError("toolspec.parameters.default() must return an instance of toolspec.parameters")
        except Exception as e:
            return TypeError(f"toolspec.parameters.default() validation failed: {e}")

        return None


    async def _setup_toolparam(self, history: History | None) -> t.PydanticFormatType:

        resp = await self.ai.ainvoke(
            instructions=self.toolparam_prompt[0].format(
                name=self.toolspec.name,
                description=self.toolspec.description
            ),
            prompt=self.toolparam_prompt[1],
            history=history,
            model=self.chosen_model,
            response_fmt=self.toolspec.parameters
        )
        if resp.error or not resp.response:
            raise resp.error or Exception("No response from AI")
        
        return resp.response


    async def arun(
        self,
        output_schema: Type[t.ToolOutputT],
        *,
        fn: Callable[..., Awaitable],
        history: History | None = None,
    ) -> ToolResponse[t.ToolOutputT]:
        
        if not callable(fn):
            return ToolResponse[t.ToolOutputT](
                output=None, 
                error=ValueError("fn must be a callable function"),
                tool_name=self.toolspec.name,
                tool_arguments=None
            )

        if not iscoroutinefunction(fn):
            return ToolResponse[t.ToolOutputT](
                output=None, 
                error=TypeError("fn must be an async function"),
                tool_name=self.toolspec.name,
                tool_arguments=None
            )

        try:
            params = await self._setup_toolparam(history=history)
        except Exception as e:
            return ToolResponse[t.ToolOutputT](
                output=None, 
                error=e,
                tool_name=self.toolspec.name,
                tool_arguments=None
            )

        try:
            resp = await fn(params)
        except Exception as e:
            return ToolResponse[t.ToolOutputT](
                output=None, 
                error=e,
                tool_name=self.toolspec.name,
                tool_arguments=params.model_dump(mode="json")
            )

        if not isinstance(resp, output_schema):
            return ToolResponse[t.ToolOutputT](
                output=None, 
                error=TypeError(f"Function return type {type(resp)} does not match expected output schema {output_schema}"),
                tool_name=self.toolspec.name,
                tool_arguments=params.model_dump(mode="json")
            )

        return ToolResponse[t.ToolOutputT](
            output=resp, 
            error=None,
            tool_name=self.toolspec.name,
            tool_arguments=params.model_dump(mode="json")
        )
    

if __name__ == "__main__":
    import asyncio
    from agents_v2.tools.registry import ai_provider, REGISTRY, WeatherResponse
    
    async def main():

        history = History()
        history.append(
            HistoryItem(
                role=RoleType.USER,
                content="오늘 서울의 날씨가 어때?"
            )
        )
        weather_reporter = REGISTRY.get_manager("weather")
        tool = REGISTRY.get_function("weather")
        output_schema = cast(type[WeatherResponse], REGISTRY.get_output_schema("weather"))

        response = await weather_reporter.arun(output_schema, fn=tool, history=history)  # Warm-up call
        
        history.append(
            HistoryItem(
                role=RoleType.TOOL,
                content=None,
                tool_calls=[
                    ToolCall(
                        id="tool_call_001",
                        name=response.tool_name,
                        arguments=response.tool_arguments or {},
                        result=str(response.output.report) if response.output else "Error"
                    )
                ]
            )
        )

        response2 = await ai_provider.ainvoke(
            instructions="Respond to the user based on the tool output.",
            prompt=None,
            history=history,
            model=ModelEnum.gpt_4o_mini,
            response_fmt=str
        )

        history.append(
            HistoryItem(
                role=RoleType.ASSISTANT,
                content=response2.response if response2.response else "No response"
            )
        )

        print(history.to_ai_message_like())
        

        

    asyncio.run(main())
