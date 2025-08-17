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
        description="현재 상황을 반영한 대화의 제목 (10자 이내) 반드시 한국어로 유효한 문자열이어야 합니다.",
        examples=["My Conversation"]
    )
    intent: str = Field(
        ...,
        description="현재 상황을 반영한 대화의 의도",
        examples=["GetWeather", "BookFlight"]
    )
    icon: str = Field(
        "😎",
        description="현재 상황을 반영한 대화의 아이콘",
        examples=["😎"]
    )
    summary: str = Field(
        "",
        description="현재 상황을 반영한 대화의 요약",
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
            intent="",
            conversation_id="<conversation_id>",
            user_id="",
            title="",
            icon="😎",
            summary="",
            messages=[]
        )
    
    def get_context(self) -> str:
        """
        Get context from the history object.
        """
        return (
f"""
---
현재까지의 사용자 의도: {self.intent}
사용자 맥락 제목: {self.title}
사용자 맥락 요약: {self.summary}
---\n
"""        
        )

    
    async def update_context(
        self, 
        current_user_message: Message,
        parent_message_id: str | None = None
    ) -> None:
        """
        Generates a context and stores it in the history object.
        
        This context can be used for further processing or analysis.
        
        Args:
            current_user_message (Message): The current user message to be added to the context.

        Returns:
            out (None) - This method does not return anything.
        """

        if parent_message_id is None:
            self.summary = current_user_message.content.parts[0]
            self.title = current_user_message.content.parts[0][:10]
            self.icon = "😎"
            self.intent = current_user_message.content.parts[0]
            return None
        
        messages = self.marshal_to_messagelike(current_user_message)
        try:
            completion = openai.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system", 
                        "content": (
f"""
## 역할 
당신은 맥락분석기입니다.

## 목표
현재 사용자에 대한 맥락과 의도를 생성하시오.
유저의 최근 메시지에 가중치를 두지만, 이전 메시지와 맥락을 고려하여 결과를 내시오.

## 이전 메시지의 맥락
{self.get_context()}
"""
                        )
                    },
                    *messages #type: ignore
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
        self.intent = context.intent


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