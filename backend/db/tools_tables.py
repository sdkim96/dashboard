import datetime as dt
from typing import Optional

from sqlalchemy import Engine
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

class ToolBase(DeclarativeBase):
    pass

class Tool(ToolBase):
    __tablename__ = 'tool'
    
    tool_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier for the tool."
    )
    name: Mapped[str] = mapped_column(
        doc="Name of the tool, unique across all tools."
    )
    description: Mapped[str] = mapped_column(
        doc="A brief description of the tool's functionality."
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        doc="Flag indicating whether the tool is active. Default is True."
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the tool was created.",
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        doc="Timestamp when the tool was last updated.",
    )
    
    def __repr__(self):
        return f"<Tool(id={self.tool_id}, name={self.name})>"