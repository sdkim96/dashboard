import datetime as dt
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field

class ConversationMaster(BaseModel):
    conversation_id: str = Field(
        ...,
        description="Unique identifier of the model.",
        examples=[str(uuid.uuid4())]
    )
    title: str = Field(
        ...,
        description="Username of the user.",
        examples=["Cool Conversation Title"]
    )
    icon: str | None = Field(
        None,
        description="Link to the user's icon or avatar, if available.",
        examples=["😎"]
    )
    created_at: dt.datetime = Field(
        ...,
        description="Creation timestamp of the conversation.",
        examples=[dt.datetime.now()]
    )
    updated_at: dt.datetime = Field(
        ...,
        description="Last updated timestamp of the conversation.",
        examples=[dt.datetime.now()]
    )