import datetime as dt
from typing import Optional

from sqlalchemy import Engine, Index
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
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        doc="Indicates whether the recommendation has been deleted."
    )

    created_at: Mapped[dt.datetime] = mapped_column()
    updated_at: Mapped[dt.datetime] = mapped_column()

    __table_args__ = (
        Index("ix_recommendation_user_id", "user_id"),
    )


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

    __table_args__ = (
        Index("ix_recommendation_agents_rec_id", "recommendation_id"),
        Index("ix_recommendation_agents_agent_id_version", "agent_id", "agent_version"),
    )


class RecommendationConversations(RecommendationsBase):
    __tablename__ = "recommendation_conversations"

    recommendation_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier for the recommendation conversation."
    )
    agent_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="The identifier of the agent associated with this recommendation conversation."
    )
    agent_version: Mapped[int] = mapped_column(
        primary_key=True,
        doc="The version of the agent associated with this recommendation conversation."
    )
    conversation_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="The identifier of the conversation associated with this recommendation."
    )
    message_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="The identifier of the message associated with this recommendation conversation."
    )

def create_recommendations_all(engine: Engine):
    """
    Creates all tables related to recommendations in the database.

    Args:
        engine (Engine): SQLAlchemy engine to connect to the database.
    """
    RecommendationsBase.metadata.create_all(bind=engine)


def drop_recommendations_all(engine: Engine):
    """
    Drops all tables related to recommendations in the database.

    Args:
        engine (Engine): SQLAlchemy engine to connect to the database.
    """
    RecommendationsBase.metadata.drop_all(bind=engine)