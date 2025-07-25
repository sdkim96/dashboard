import datetime as dt

from sqlalchemy import Engine
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

class ToolBase(DeclarativeBase):
    pass

class Tool(ToolBase):
    __tablename__ = 'tools'
    
    tool_id: Mapped[str] = mapped_column(
        primary_key=True,
    )
    author_id: Mapped[str] = mapped_column(
        nullable=False,
        doc="Foreign key referencing the user who created the tool."
    )
    tool_name: Mapped[str] = mapped_column(
        nullable=False, 
        doc="Name of the tool."
    )
    description: Mapped[str] = mapped_column(   
        nullable=False, 
        doc="Description of the tool."
    )
    icon_link: Mapped[str] = mapped_column(
        nullable=True,
        doc="Link to the icon representing the tool. It can be a URL or a path."
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        doc="Flag indicating whether the tool is deleted. Default is False."
    )
    created_at: Mapped[dt.datetime] = mapped_column()
    updated_at: Mapped[dt.datetime] = mapped_column()

    def __repr__(self):
        return f"<Tool(tool_id={self.tool_id}, name={self.tool_name})>"
    

class ToolSubscriber(ToolBase):
    __tablename__ = 'tool_subscriber'
    
    tool_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="Foreign key referencing the tool this subscription belongs to."
    )
    user_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="Foreign key referencing the user who subscribed to the tool."
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        default=dt.datetime.now,
        doc="Timestamp when the subscription was created."
    )

    def __repr__(self):
        return f"<ToolSubscriber(tool_id={self.tool_id}, user_id={self.user_id})>"
    

def create_tool_all(engine: Engine):
    ToolBase.metadata.create_all(engine)

def drop_tool_all(engine: Engine):
    ToolBase.metadata.drop_all(engine)