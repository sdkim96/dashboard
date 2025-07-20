from typing import List
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
    

    def marshal_to_messagelike(self, user_message: Message) -> List[dict]:
        """
        Marshals the history messages into a list of dictionaries suitable for
        use with a message-like interface.

        Message-Like is a message form that many issuers choose to interact.
        The format is:
        ```json
        {
            "role": "user" | "assistant",
            "content": "The content of the message"
        }
        ```
        
        Args:
            user_message (Message): The user message to be added to the history.
        
        Returns:
            List[dict]: A list of dictionaries representing the messages.
        """
        marshalled_messages = []
        for msg in self.messages:
            marshalled = {}
            role = msg.role
            content = msg.content.parts[0]
            
            marshalled["role"] = role
            marshalled["content"] = content
            marshalled_messages.append(marshalled)

        if user_message:
            marshalled = {}
            marshalled["role"] = user_message.role
            marshalled["content"] = user_message.content.parts[0]
            marshalled_messages.append(marshalled)

        return marshalled_messages