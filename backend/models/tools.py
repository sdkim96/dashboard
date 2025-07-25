import datetime as dt
import uuid

from pydantic import BaseModel, Field

class ToolMaster(BaseModel):
    tool_id: str = Field(
        ..., 
        description="Unique identifier for the tool."
    )
    tool_name: str = Field(
        ..., 
        description="Name of the tool."
    )
    author_name: str = Field(
        ..., 
        description="Name of the author who created the tool."
    )
    icon_link: str | None = Field(
        None, 
        description="Link to the icon representing the tool. It can be a URL or a path."
    )
    subscribed_count: int = Field(
        default=0,
        description="Number of users subscribed to this tool."
    )
    created_at: dt.datetime = Field(
        default_factory=dt.datetime.now, 
        description="Timestamp when the tool was created."
    )
    updated_at: dt.datetime = Field(
        default_factory=dt.datetime.now, 
        description="Timestamp when the tool was last updated."
    )

    @classmethod
    def mock(cls) -> "ToolMaster":
        """Creates a mock Tool instance for testing."""
        return cls(
            tool_id=str(uuid.uuid4()),
            tool_name="Mock Tool",
            author_name="Mock Author",
            icon_link="http://example.com/icon.png",
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now()
        )

class Tool(ToolMaster):
    description: str = Field(
        ..., 
        description="Description of the tool."
    ) 

    @classmethod
    def mock(cls) -> "Tool":
        """Creates a mock Tool instance for testing."""
        return cls(
            tool_id=str(uuid.uuid4()),
            tool_name="Mock Tool",
            author_name="Mock Author",
            description="This is a mock tool for testing purposes.",
            icon_link="http://example.com/icon.png",
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now()
        )
    
class ToolRequest(BaseModel):
    tool_id: str = Field(
        ..., 
        description="Unique identifier for the tool."
    )

    @classmethod
    def mock(cls) -> "ToolRequest":
        """Creates a mock ToolRequest instance for testing."""
        return cls(
            tool_id=str(uuid.uuid4()),
        )