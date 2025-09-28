import enum
import json
from typing import List

from pydantic import BaseModel, Field

from agents_v2.tools.spec import ToolCall
from agents_v2.providers.constants import ProviderType


class RoleType(str, enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class HistoryItem(BaseModel):
    role: RoleType = Field(
        ...,
        description="메세지 송신자의 역할"
    )
    content: str | None = Field(
        ...,
        description="내용 (텍스트)"
    )
    tool_calls: List[ToolCall] | None = Field(
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


    def to_ai_message_like(self, provider: ProviderType = ProviderType.OPENAI) -> List[dict]:
        """

        """
        messages: List[dict] = []
        for item in self:
            if item.role in {
                RoleType.USER, 
                RoleType.ASSISTANT, 
                RoleType.SYSTEM
            }:
                message = {
                    "role": item.role.value, 
                    "content": item.content or ""
                }
                messages.append(message)
                continue
            
            if item.tool_calls is None:
                raise ValueError("Tool calls must be provided for tool interactions.")
            
            if provider == ProviderType.OPENAI:

                result_messages = []
                for call in item.tool_calls:
                    call_dict = {
                        "arguments": json.dumps(call.arguments, ensure_ascii=False),
                        "call_id": call.id,
                        "name": call.name,
                        "type": "function_call",
                    }
                    result_messages.append(call_dict)

                    result_dict = {
                        "type": "function_call_output",
                        "call_id": call.id,
                        "output": call.result
                    }
                    result_messages.append(result_dict)

                messages.extend(result_messages)
        
        return messages
        