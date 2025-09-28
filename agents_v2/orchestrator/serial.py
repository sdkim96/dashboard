import enum
from typing import Tuple, Literal

from pydantic import Field

import agents_v2.types as t

from agents_v2.providers.base import BaseProvider
from agents_v2.providers.openai import OpenAIModelEnum
from agents_v2.tools.registry import ToolRegistry


class SerialOrchestrator:

    class _ToolChoiceResponse(t.PydanticFormatType):
        tool_name: str = Field(..., description="선택한 도구의 이름")
        reason: str = Field(..., description="도구를 선택한 이유")
        score: int = Field(..., ge=1, le=10, description="1~10 사이의 점수로, 높을수록 더 적절한 도구임을 의미")

        @classmethod
        def default(cls) -> "SerialOrchestrator._ToolChoiceResponse":
            return SerialOrchestrator._ToolChoiceResponse(
                tool_name="weather",
                reason="Default weather tool",
                score=1
            )
        
    class _Plan(t.PydanticFormatType):
        next: str = Field(..., description="선택한 툴 또는 에이전트의 이름")
        type: Literal['tool', 'agent'] = Field(..., description="다음 단계에 호출할 대상의 유형 (tool 또는 agent)")
        reason: str = Field(..., description="다음번 툴 또는 에이전트를 선택한 이유")

        @classmethod
        def default(cls) -> "SerialOrchestrator._Plan":
            return SerialOrchestrator._Plan(
                next="weather",
                type="tool",
                reason="Default weather tool"
            )

    def __init__(
        self,
        provider: BaseProvider,
        tool_registry: ToolRegistry,
        agent_registry,
    ) -> None:
        self.provider = provider
        self.tool_registry = tool_registry
        self.agent_registry = agent_registry

    @property
    def plan_prompt(self) -> Tuple[str, str]:
        return (
"""
## 역할
당신은 매우 유능한 계획 수립자입니다. 

## 목적
당신의 목적은 주어진 유저의 질문을 해결하기 위해 사용된 도구 및 에이전트의 결과를 기반으로 다음 단계를 계획하는 것입니다.

## 해결해야 할 유저의 질문
{user_question}

## 유저의 맥락
{user_context}

## 도구 결과
{tool_results}

## 에이전트 결과
{agent_results}

""",
"""
결과를 확인하고 다음 단계를 계획하세요.
"""
        )
    
    @property
    def tool_choice_prompt(self) -> Tuple[str, str]:
        return (
"""
## 역할
당신은 매우 유능한 AI 도구 선택기입니다.

## 목적
당신의 목적은 주어진 도구 설명과 유저의 질문을 기반으로 적절한 도구를 선택하는 것입니다.

## 도구 설명
{tool_descriptions}
""",
"""
가장 적절한 도구를 하나 선택해주세요.
"""
        )
    
    @property
    def chosen_model(self) -> enum.Enum:
        if self.provider.provider_name == "openai":
            model = OpenAIModelEnum.gpt_4o_mini
        else:
            raise ValueError(f"Unsupported provider: {self.provider.provider_name}")
        return model
    
    async def _aplan(self):
        plan = await self.provider.ainvoke(
            instructions=self.tool_choice_prompt[0].format(
                user_question=self.tool_registry.descriptions(),
                user_context="",
                tool_results="",
                agent_results=""
            ),
            prompt=self.tool_choice_prompt[1],
            history=history,
            model=self.chosen_model,
            response_fmt=self._Plan
        )
    

    async def arun(self, history):
        """
        유저의 질문 분석
        1. 도구가 필요하다면 어떤 도구가 필요한지 판단 (LLM)
        2. 도구를 호출하고 결과를 받아옴
        4. 도구의 결과를 바탕으로 유저에게 답변
        5. 도구가 더 필요하다면 1번으로 돌아감
        6. 특정 에이전트의 도움이 필요하다면 해당 에이전트에게 물어봄
        """

        tool_to_use = await self.provider.ainvoke(
            instructions=self.tool_choice_prompt[0].format(
                tool_descriptions=self.tool_registry.descriptions()
            ),
            prompt=self.tool_choice_prompt[1],
            history=history,
            model=self.chosen_model,
            response_fmt=self._ToolChoiceResponse
        )
        if tool_to_use.response is None:
            raise ValueError("No tool selected")
        tool = tool_to_use.response
        yield {'tool_choice': tool_to_use.response}
        
        fn = self.tool_registry.get_function(tool.tool_name)
        mng = self.tool_registry.get_manager(tool.tool_name)
        output_schema = self.tool_registry.get_output_schema(tool.tool_name)

        tool_result = await mng.arun(output_schema=output_schema, fn=fn, history=history)
        yield {'tool_result': tool_result}





        

        