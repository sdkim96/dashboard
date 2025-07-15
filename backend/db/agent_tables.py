import datetime as dt
from typing import Optional

from sqlalchemy import Engine
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

class AgentBase(DeclarativeBase):
    pass

class AgentMaster(AgentBase):
    __tablename__ = 'agent_master'
    
    agent_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier exposed to clients."
    )
    author_id: Mapped[int] = mapped_column(
        doc="The author of the agent. User table's id is used as a foreign key."
    )
    name: Mapped[str] = mapped_column(
        doc="Name of the agent, unique across all agents."
    )
    issuer: Mapped[str] = mapped_column(
        doc="The issuer of the agent, typically the organization or individual who created it."
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
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        doc="Unique identifier for the agent detail. It is automatically generated integer."
    )
    agent_id: Mapped[int] = mapped_column(
        unique=True,
        doc="Foreign key referencing the agent this detail belongs to. It is a foreign key to agent_master table."
    )
    prompt: Mapped[str] = mapped_column(
        doc="The prompt used by the agent to generate responses. It can include placeholders for dynamic content."
    )
    input_schema: Mapped[str] = mapped_column(
        doc="Schema of the output produced by the agent. Marshaled as JSON string. It can be unmarshalled to a Python dictionary."
    )
    output_schema: Mapped[str] = mapped_column(
        doc="Schema of the output produced by the agent. Marshaled as JSON string. It can be unmarshalled to a Python dictionary."
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the agent detail was created."
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the agent detail was last updated."
    )

    def __repr__(self):
        return f"<AgentDetail(id={self.id}, agent_id={self.agent_id})>"
   

class AgentTag(AgentBase):
    __tablename__ = 'agent_tag'
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        doc="Unique identifier for the agent tag."
    )
    agent_id: Mapped[int] = mapped_column(
        doc="Foreign key referencing the agent this tag belongs to.",
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
    
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
        doc="Unique identifier for the agent subscriber."
    )
    agent_id: Mapped[int] = mapped_column(
        doc="Foreign key referencing the agent this subscriber belongs to.",
    )
    user_id: Mapped[int] = mapped_column(
        doc="Foreign key referencing the user who subscribed to the agent.",
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the agent subscription was created."
    )
    
    def __repr__(self):
        return f"<AgentSubscriber(id={self.id}, agent_id={self.agent_id}, user_id={self.user_id})>"

def create_agent_all(engine: Engine):
    AgentBase.metadata.create_all(engine)