import datetime as dt

from sqlalchemy import Engine, Index
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

class ToolBase(DeclarativeBase):
    pass

class Tool(ToolBase):
    __tablename__ = 'tools'
    
    tool_id: Mapped[str] = mapped_column(primary_key=True)
    author_id: Mapped[str] = mapped_column(
        nullable=False,
        doc="Foreign key referencing the user who created the tool.",
        index=True,
    )
    tool_name: Mapped[str] = mapped_column(
        nullable=False, 
        doc="Name of the tool.",
        index=True,
    )
    description: Mapped[str] = mapped_column(nullable=False, doc="Description of the tool.")
    icon_link: Mapped[str] = mapped_column(nullable=True, doc="Tool icon link.")
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        doc="Soft delete flag.",
        index=True,
    )
    created_at: Mapped[dt.datetime] = mapped_column(index=True)
    updated_at: Mapped[dt.datetime] = mapped_column(index=True)

    __table_args__ = (

        Index("ix_tools_author_deleted", "author_id", "is_deleted"),
        Index("ix_tools_author_updated", "author_id", "updated_at"),
    )

    def __repr__(self):
        return f"<Tool(tool_id={self.tool_id}, name={self.tool_name})>"


class ToolResult(ToolBase):
    __tablename__ = 'tool_results'

    conversation_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="FK to conversation.",
    )
    message_id: Mapped[str] = mapped_column(
        primary_key=True,
    )
    tool_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="FK to tool.",
    )
    output: Mapped[str] = mapped_column(nullable=False, doc="Tool output.")
    created_at: Mapped[dt.datetime] = mapped_column(index=True)
    updated_at: Mapped[dt.datetime] = mapped_column(index=True)

    __table_args__ = (
        Index("ix_tool_results_conv_msg", "conversation_id", "message_id"),
        Index("ix_tool_results_conv_created", "conversation_id", "created_at"),
        Index("ix_tool_results_msg_tool", "message_id", "tool_id"),
        Index("ix_tool_results_conv_tool", "conversation_id", "tool_id"),
    )

    def __repr__(self):
        return f"<ToolResult(message_id={self.message_id}, tool_id={self.tool_id})>"

def create_tool_all(engine: Engine):
    ToolBase.metadata.create_all(engine)

def drop_tool_all(engine: Engine):
    ToolBase.metadata.drop_all(engine)