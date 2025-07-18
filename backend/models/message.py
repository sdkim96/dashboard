import datetime as dt
import uuid

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

class Message(BaseModel):
    """
    Message model representing a single message in a conversation.
    """
    message_id: str = Field(
        ...,
        description="Unique identifier of the message.",
        examples=["message-123"]
    )
    parent_message_id: str | None = Field(
        None,
        description="ID of the parent message, if this message is a reply.",
        examples=["parent-message-123"]
    )
    agent_id: str | None = Field(
        None,
        description="ID of the agent that sent the message, if applicable.",
        examples=["agent-123"]
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
    model: str = Field(
        ...,
        description="The model used to generate the message.",
        examples=["gpt-3.5-turbo"]
    )
    created_at: dt.datetime = Field(
        ...,
        description="Creation timestamp of the message.",
        examples=["2023-10-01T12:00:00Z"]
    )
    updated_at: dt.datetime = Field(
        ...,
        description="Last updated timestamp of the message.",
        examples=["2023-10-01T12:00:00Z"]
    )

    @classmethod
    def user_message(
        cls, 
        message_id: str,
        parent_message_id: str | None,
        agent_id: str | None,
        content: Content, 
        model: str, 
    ) -> 'Message':
        """
        Create a user message instance.
        """
        return cls(
            message_id=message_id,
            parent_message_id=parent_message_id,
            agent_id=agent_id,
            role='user',
            content=content,
            model=model,
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now()
        )

    @classmethod
    def assistant_message(
        cls, 
        message_id: str,
        parent_message_id: str | None,
        agent_id: str | None,
        content: Content, 
        model: str, 
    ) -> 'Message':
        """
        Create an assistant message instance.
        """
        return cls(
            message_id=message_id,
            parent_message_id=parent_message_id,
            agent_id=agent_id,
            role='assistant',
            content=content,
            model=model,
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now()
        )
