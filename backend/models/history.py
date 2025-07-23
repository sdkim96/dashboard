from typing import List

import openai
from pydantic import BaseModel, Field

from backend.models.message import Message
from backend.utils import logger as lg

class Context(BaseModel):
    """
    Represents the context of a conversation.
 
    """
    title: str = Field(
        ...,
        description="Title of the conversation.",
        examples=["My Conversation"]
    )
    icon: str = Field(
        "😎",
        description="Icon representing the conversation.",
        examples=["😎"]
    )
    summary: str = Field(
        "",
        description="Summary of the conversation.",
        examples=["This is a summary of the conversation."]
    )

class History(Context):
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
            icon="😎",
            summary="",
            messages=[]
        )
    
    async def update_context(self, current_user_message: Message) -> None:
        """
        Generates a context and stores it in the history object.
        
        This context can be used for further processing or analysis.
        
        Args:
            current_user_message (Message): The current user message to be added to the context.

        Returns:
            out (None) - This method does not return anything.
        """
        
        messages = self.marshal_to_messagelike(current_user_message)
        try:
            completion = openai.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"You are a helpful assistant. Generate a context from the conversations. current user message: {current_user_message.content.parts[0]}"},
                    *messages
                ],
                response_format=Context
            )
        except Exception as e:
            lg.logger.error(f"Error generating context: {e}")
            return
        
        context = completion.choices[0].message.parsed
        if not context:
            lg.logger.warning("Generated context is empty.")
            return
        
        self.summary = context.summary
        self.title = context.title
        self.icon = context.icon


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