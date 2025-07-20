import datetime as dt
from typing import Optional

from sqlalchemy import Engine
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

class AgentBase(DeclarativeBase):
    pass

class Agent(AgentBase):
    __tablename__ = 'agent'
    
    agent_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier exposed to clients."
    )
    author_id: Mapped[str] = mapped_column(
        doc="The author of the agent. User table's id is used as a foreign key."
    )
    name: Mapped[str] = mapped_column(
        doc="Name of the agent, unique across all agents."
    )
    icon_link: Mapped[Optional[str]] = mapped_column(
        doc="Link to the icon representing the agent. It can be a URL or a path"
    )
    description: Mapped[str] = mapped_column(
        doc="A brief description of the agent's purpose or functionality."
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        doc="Flag indicating whether the agent is deleted. Default is False."
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        doc="Flag indicating whether the agent is active. Default is True."
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the agent was created.",
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the agent was last updated.",
    )
    
    def __repr__(self):
        return f"<Agent(id={self.agent_id}, name={self.name})>"

 
class AgentDetail(AgentBase):
    __tablename__ = 'agent_detail'
    
    agent_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="Foreign key referencing the agent this detail belongs to. It is a foreign key to agent_master table."
    )
    version: Mapped[int] = mapped_column(
        primary_key=True,
        doc="Version of the agent detail. It is incremented when the agent detail is updated."
    )
    prompt: Mapped[str] = mapped_column(
        doc="The prompt used by the agent to generate responses. It can include placeholders for dynamic content."
    )
    output_schema: Mapped[Optional[str]] = mapped_column(
        doc="Schema of the output produced by the agent. Marshaled as JSON string. It can be unmarshalled to a Python dictionary." \
        " If not provided, it will be treated as a raw string."
    )    
    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the agent detail was created."
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the agent detail was last updated."
    )

    def __repr__(self):
        return f"<AgentDetail(agent_id={self.agent_id}, version={self.version})>"
   

class AgentTag(AgentBase):
    __tablename__ = 'agent_tag'
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        doc="Unique identifier for the agent tag."
    )
    agent_id: Mapped[str] = mapped_column(
        doc="Foreign key referencing the agent this tag belongs to.",
    )
    agent_version: Mapped[int] = mapped_column(
        doc="Version of the agent this tag is associated with."
    )
    tag: Mapped[str] = mapped_column(
        doc="Tag associated with the agent, used for categorization or search.",
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the agent tag was created."
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the agent tag was last updated."
    )
    
    def __repr__(self):
        return f"<AgentTag(id={self.id}, agent_id={self.agent_id}, tag={self.tag})>"

class AgentSubscriber(AgentBase):
    __tablename__ = 'agent_subscriber'
    
    user_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="Foreign key referencing the user who subscribed to the agent.",
    )
    agent_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="Foreign key referencing the agent this subscriber belongs to.",
    )
    agent_version: Mapped[int] = mapped_column(
        doc="Version of the agent this subscriber is subscribed to."
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the agent subscription was created."
    )
    
    def __repr__(self):
        return f"<AgentSubscriber(agent_id={self.agent_id}, user_id={self.user_id})>"


class AgentPrivacy(AgentBase):
    __tablename__ = 'agent_privacy'

    agent_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="Foreign key referencing the agent. Each agent can have one hide config."
    )
    
    hide_author: Mapped[bool] = mapped_column(
        default=False,
        doc="If True, the author's identity is hidden."
    )
    
    hide_prompt: Mapped[bool] = mapped_column(
        default=False,
        doc="If True, the agent's prompt is hidden."
    )

    reason: Mapped[Optional[str]] = mapped_column(
        doc="Optional reason for hiding the information. Can be displayed to end users if needed."
    )

    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the hide configuration was created."
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the hide configuration was last updated."
    )

    def __repr__(self):
        return f"<AgentHide(agent_id={self.agent_id}, hide_author={self.hide_author}, hide_prompt={self.hide_prompt})>"

def create_agent_all(engine: Engine):
    AgentBase.metadata.create_all(engine)

def drop_agent_all(engine: Engine):
    AgentBase.metadata.drop_all(engine)