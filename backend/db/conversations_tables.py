import datetime as dt
from typing import Optional

from sqlalchemy import Engine
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

class ConversationBase(DeclarativeBase):
    pass

class Conversation(ConversationBase):
    __tablename__ = 'conversation'

    conversation_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier exposed to clients."
    )
    user_id: Mapped[int] = mapped_column(
        doc="The user who initiated the conversation. User table's id is used as a foreign key."
    )
    title: Mapped[str] = mapped_column(
        doc="Title of the conversation, unique across all conversations."
    )
    summary: Mapped[Optional[str]] = mapped_column(
        doc="A brief summary of the conversation's content."
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        doc="Flag indicating whether the conversation is deleted. Default is False."
    )
    icon: Mapped[Optional[str]] = mapped_column(
        doc="Link to the icon representing the conversation. It can be a URL or a path"
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the conversation was created.",
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the conversation was last updated.",
    )
    
    def __repr__(self):
        return f"<Conversation(id={self.conversation_id}, title={self.title})>"
    

class Message(ConversationBase):
    __tablename__ = 'message'

    message_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier for the message in the conversation."
    )
    conversation_id: Mapped[str] = mapped_column(
        doc="Foreign key referencing the conversation this detail belongs to. It is a foreign key to conversations_master table."
    )
    parent_message_id: Mapped[Optional[str]] = mapped_column(
        doc="The ID of the parent message in the conversation. It can be None for root messages."
    )
    agent_id: Mapped[Optional[str]] = mapped_column(
        doc="The ID of the agent that sent the message. It can be None if the message is from a user."
    )
    role: Mapped[str] = mapped_column(
        doc="Role of the message sender, e.g., 'user' or 'assistant'."
    )
    content: Mapped[str] = mapped_column(
        doc="The content of the message in the conversation."
    )
    model: Mapped[str] = mapped_column(
        doc="The model used to generate the message. It can be a specific model name"
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the message was created.",
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the message was last updated.",
    )
    
    def __repr__(self):
        return f"<Message(id={self.message_id}, conversation_id={self.conversation_id})>"
    


def create_conversations_all(engine: Engine):
    """
    Creates all tables related to conversations in the database.
    
    Args:
        engine (Engine): SQLAlchemy engine to connect to the database.
    """
    ConversationBase.metadata.create_all(bind=engine)