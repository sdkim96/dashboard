import datetime as dt
from typing import Optional

from sqlalchemy import Engine
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

class RecommendationsBase(DeclarativeBase):
    pass

class Recommendation(RecommendationsBase):
    __tablename__ = "recommendation"

    recommendation_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier for the recommendation."
    )
    title: Mapped[str] = mapped_column(
        doc="Title of the recommendation, unique across all recommendations."
    )
    description: Mapped[str] = mapped_column(
        doc="A brief description of the recommendation's content."
    )
    user_id: Mapped[str] = mapped_column(
        doc="The user who initiated the recommendation. User table's id is used as a foreign key."
    )
    work_when: Mapped[dt.datetime] = mapped_column(
        doc="The date and time when the recommendation is intended to be worked on."
    )
    work_where: Mapped[str] = mapped_column(
        doc="The location where the recommendation is intended to be worked on."
    )
    work_whom: Mapped[str] = mapped_column(
        doc="The person or team with whom the recommendation is intended to be worked on."
    )
    work_details: Mapped[str] = mapped_column(
        doc="Detailed information about the work associated with the recommendation."
    )

    created_at: Mapped[dt.datetime] = mapped_column()
    updated_at: Mapped[dt.datetime] = mapped_column()


class RecommendationAgents(RecommendationsBase):
    __tablename__ = "recommendation_agents"

    recommendation_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier for the recommendation detail."
    )
    agent_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="The identifier of the agent associated with this recommendation."
    )
    agent_version: Mapped[int] = mapped_column(
        primary_key=True,
        doc="The version of the agent associated with this recommendation."
    )
    created_at: Mapped[dt.datetime] = mapped_column()
    updated_at: Mapped[dt.datetime] = mapped_column()


class RecommendationMessage(RecommendationsBase):
    __tablename__ = "recommendation_message"

    message_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="The identifier of the message associated with this recommendation."
    )
    recommendation_id: Mapped[str] = mapped_column(
        doc="A unique identifier for the recommendation message."
    )
    parent_message_id: Mapped[Optional[str]] = mapped_column(
        doc="The identifier of the parent message in the conversation, if applicable."
    )
    agent_id: Mapped[str] = mapped_column(
        doc="The identifier of the agent associated with this recommendation message."
    )
    agent_version: Mapped[int] = mapped_column(
        doc="The version of the agent associated with this recommendation message."
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