import uuid
from typing import List

from pydantic import BaseModel, Field
from backend.models.v2.tools import ToolRequest



class PostCompletionV2Request(BaseModel):
    prompt: str = Field(
        ...,
        description="유저의 질문 (프롬프트)",
        examples=["Hello, how are you?"]
    )
    parent_message_id: str | None = Field(
        default=None,
        description="요청에 대한 부모 메시지 ID",
        examples=[str(uuid.uuid4())]
    )
    tools: List[ToolRequest] = Field(
        default_factory=list,
        description="생성에 사용될 도구 목록",
        examples=[[ToolRequest.mock()]]
    )
    llm: LLMModelRequest = Field(
        ...,
        description="모델 배포 ID (Deployment ID)",
        examples=[LLMModelRequest(
            issuer="openai",
            deployment_id="deployment-123",
        )]
    )