from enum import Enum
from typing import Awaitable, Callable, Type, Tuple
from inspect import iscoroutinefunction, getattr_static

import agents_v2.types as t

from agents_v2.providers.base import BaseProvider
from agents_v2.providers.openai import ModelEnum
from agents_v2.tools.spec import ToolSpec, ToolResponse, ToolType
from agents_v2.utils.history import History, HistoryItem


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
            return ToolResponse[t.ToolOutputT](output=None, error=ValueError("fn must be a callable function"))

        if not iscoroutinefunction(fn):
            return ToolResponse[t.ToolOutputT](output=None, error=TypeError("fn must be an async function"))

        try:
            params = await self._setup_toolparam(history=history)
        except Exception as e:
            return ToolResponse[t.ToolOutputT](output=None, error=e)

        try:
            resp = await fn(params)
        except Exception as e:
            return ToolResponse[t.ToolOutputT](output=None, error=e)

        if not isinstance(resp, output_schema):
            return ToolResponse[t.ToolOutputT](output=None, error=TypeError(f"Function return type {type(resp)} does not match expected output schema {output_schema}"))

        return ToolResponse[t.ToolOutputT](output=resp, error=None)
    

if __name__ == "__main__":
    import asyncio
    from pydantic import Field, BaseModel
    from agents_v2.providers.openai import OpenAIProvider
    from openai import AsyncOpenAI
    from agents_v2.utils.constants import RoleType
    

    class RandomSumInput(t.PydanticFormatType):
        a: int = Field(..., description="An integer parameter.")
        b: int = Field(..., description="Another integer parameter.")

        @classmethod
        def default(cls) -> "RandomSumInput":
            return RandomSumInput(a=1, b=2)

    class RandomSumOutput(BaseModel):
        result : int = Field(..., description="The sum of a and b.")

    async def example_tool_fn(params: RandomSumInput) -> RandomSumOutput:
        return RandomSumOutput(result=params.a + params.b)


    async def main():

        ai_provider = OpenAIProvider(client=AsyncOpenAI())

        history = History()
        history.append(HistoryItem(
            role=RoleType.USER,
            content="1과 2를 더해줘"
        ))
        toolspec = ToolSpec(
            name="ExampleSearchTool",
            type=ToolType.calculator,
            description="A tool to perform a search operation based on a query string.",
            parameters=RandomSumInput
        )
        tool_manager = ToolManager(ai=ai_provider, toolspec=toolspec)

        response = await tool_manager.arun(
            RandomSumOutput, 
            fn=example_tool_fn,
            history=history
        )
        if response.error:
            print(f"Error: {response.error}")
        else:
            print(f"Output: {response.output.result if response.output else response.output}")

        

    asyncio.run(main())
