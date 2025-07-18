from pydantic import BaseModel, Field
from backend.models.message import Message

class History(BaseModel):
    conversation_id: str = Field(
        ...,
        description="Unique identifier of the conversation.",
        examples=["conversation-123"]
    )
    user_id: str = Field(
        ...,
        description="Unique identifier of the user.",
        examples=["user-123"]
    )
    title: str = Field(
        ...,
        description="Title of the conversation.",
        examples=["My Conversation"]
    )
    summary: str = Field(
        ...,
        description="Summary of the conversation.",
        examples=["This is a summary of the conversation."]
    )
    messages: list[Message] = Field(
        ...,
        description="List of messages in the conversation."
    )

    @property
    def is_empty(self) -> bool:
        """
        Returns True if this conversation has no messages.
        """
        return len(self.messages) == 0

    @classmethod
    def failed(cls) -> "History":
        """
        Returns a failed history object with empty fields.
        
        This is useful for indicating that the history retrieval failed.
        """
        return cls(
            conversation_id="",
            user_id="",
            title="",
            summary="",
            messages=[]
        )
