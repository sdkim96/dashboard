from typing import List
from pydantic import BaseModel, Field

import backend._types as t

class Content(BaseModel):
    """
    Content model for messages
    """
    type: t.MessageContentType = Field(
        default='text',
        description="Type of the message content, e.g., 'text'.",
        examples=["text"]
    )
    parts: List[str] = Field(
        default_factory=list,
        description="List of parts that make up the message content.",
        examples=[["Hello, how can I help you?"]]
    )

class MessageRequest(BaseModel):
    content: Content

class MessageResponse(BaseModel):
    """
    Response model for messages
    """
    message_id: str = Field(
        ...,
        description="Unique identifier of the message.",
        examples=["message-123"]
    )
    role: t.MessageRoleLiteral = Field(
        ...,
        description="Role of the message sender, e.g., 'user' or 'assistant'.",
        examples=["user", "assistant"]
    )
    content: Content = Field(
        ...,
        description="Content of the message.",
        examples=[Content(type='text', parts=["Hello, how can I help you?"])]
    )
    created_at: str = Field(
        ...,
        description="Creation timestamp of the message.",
        examples=["2023-10-01T12:00:00Z"]
    )
    updated_at: str = Field(
        ...,
        description="Last updated timestamp of the message.",
        examples=["2023-10-01T12:00:00Z"]
    )
    parent_message_id: str | None = Field(
        None,
        description="ID of the parent message, if this message is a reply.",
        examples=["parent-message-123"]
    )
