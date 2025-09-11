from typing import List

from pydantic import BaseModel, Field

import agents_v2.utils.constants as c

class HistoryItem(BaseModel):
    role: c.RoleType = Field(
        ...,
        description="메세지 송신자의 역할"
    )
    content: str | None = Field(
        ...,
        description="내용 (텍스트)"
    )
    tool_calls: List[c.ToolCall] | None = Field(
        default=None,
        description="도구 호출 정보 (도구 사용 및 결과)"
    )

class History(list[HistoryItem]):

    def __init__(self) -> None:
        super().__init__()


    def append(self, item: HistoryItem) -> None:
        if not isinstance(item, HistoryItem):
            raise ValueError("Only HistoryItem instances can be added to History.")
        
        super().append(item)


    def to_ai_message_like(self, provider: c.ProviderType = c.ProviderType.OPENAI) -> List[dict]:
        """
        ## OPENAI 예시
        messages = [
            {"role": "user", "content": "안녕!"},
            {"role": "assistant", "content": "반가워요!"},
            {"role": "assistant", "tool_calls": [{"id": "call_1", "name": "get_weather", "arguments": "{}"}]},
            {"role": "tool", "tool_call_id": "call_1", "content": "날씨는 맑음"}
        ]

        ## ANTHROPIC 예시
        messages = [
            {"role": "user", "content": "안녕!"},
            {"role": "assistant", "content": "반가워요!"},
            {"role": "assistant", "content": [
                {"type": "tool_use", "id": "toolu_01", "name": "get_weather", "input": {}}
            ]},
            {"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": "toolu_01", "content": "날씨는 맑음"}
            ]}
        ]
        """
        messages: List[dict] = []
        for item in self:
            if item.role in {
                c.RoleType.USER, 
                c.RoleType.ASSISTANT, 
                c.RoleType.SYSTEM
            }:
                message = {
                    "role": item.role.value, 
                    "content": item.content or ""
                }
                messages.append(message)
                continue
            
            if item.tool_calls is None:
                raise ValueError("Tool calls must be provided for tool interactions.")
            
            if provider == c.ProviderType.OPENAI:

                calls = []
                result_messages = []
                for call in item.tool_calls:
                    call_dict = {
                        "id": call.id,
                        "name": call.name,
                        "arguments": call.arguments
                    }
                    calls.append(call_dict)

                    result_dict = {
                        "role": c.RoleType.TOOL.value,
                        "tool_call_id": call.id,
                        "content": call.result or ""
                    }
                    result_messages.append(result_dict)

                call_message = {
                    "role": c.RoleType.ASSISTANT.value, 
                    "tool_calls": calls
                }

                messages.append(call_message)
                messages.extend(result_messages)
        
        return messages
        