import datetime as dt
from typing import Optional

from sqlalchemy import Engine
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

from backend.models.message import Content

class ConversationBase(DeclarativeBase):
    pass

class LLMIssuer(ConversationBase):
    __tablename__ = 'llm_issuer'

    deployment_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="The unique identifier for the LLM deployment, e.g., 'gpt-4o-mini'."
    )
    issuer: Mapped[str] = mapped_column(
        doc="The name of the LLM provider, e.g., 'openai', 'anthropic'."
    )
    name: Mapped[str] = mapped_column(
        doc="The name of the LLM model, e.g., 'GPT-4o Mini'."
    )
    description: Mapped[str] = mapped_column(
        doc="A brief description of the LLM provider."
    )
    icon_link: Mapped[Optional[str]] = mapped_column(
        doc="Link to the icon representing the LLM provider."
    )
    
    def __repr__(self):
        return f"<LLMProvider(issuer={self.issuer}, deployment_id={self.deployment_id})>"

class Conversation(ConversationBase):
    __tablename__ = 'conversation'

    conversation_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier exposed to clients."
    )
    user_id: Mapped[str] = mapped_column(
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
    conversation_type: Mapped[str] = mapped_column(
        doc="Type of the conversation, e.g., 'chat', 'recommendation'."
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
    tool_id: Mapped[Optional[str]] = mapped_column(
        doc="The ID of the tool used to generate the message, if applicable."
    )
    role: Mapped[str] = mapped_column(
        doc="Role of the message sender, e.g., 'user' or 'assistant'."
    )
    content: Mapped[str] = mapped_column(
        doc="The content of the message in the conversation."
    )
    llm_deployment_id: Mapped[Optional[str]] = mapped_column(
        doc="The llm_model used to generate the message. It can be a specific model name"
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the message was created.",
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the message was last updated.",
    )
    
    def __repr__(self):
        return f"<Message(message_id={self.message_id}, conversation_id={self.conversation_id})>"
    
    


def create_conversations_all(engine: Engine):
    """
    Creates all tables related to conversations in the database.
    
    Args:
        engine (Engine): SQLAlchemy engine to connect to the database.
    """
    ConversationBase.metadata.create_all(bind=engine)


def drop_conversations_all(engine: Engine):
    """
    Drops all tables related to conversations in the database.
    
    Args:
        engine (Engine): SQLAlchemy engine to connect to the database.
    """
    ConversationBase.metadata.drop_all(bind=engine)