from typing import List, Optional
from pydantic import BaseModel, Field

class Agent(BaseModel):
    agent_id: str = Field(
        ...,
        description="Unique identifier of the model.",
        examples=["user-123"]
    )
    name: str = Field(
        ...,
        description="Username of the user.",
        examples=["example_user"]
    )
    tags: List[str] = Field(
        default_factory=list,
        description="List of tags associated with the agent.",
        examples=[["tag1", "tag2"]]
    )
    icon_link: str | None = Field(
        None,
        description="Link to the user's icon or avatar, if available.",
        examples=["https://example.com/icon.png"]
    )


class AgentPublish(BaseModel):
    
    name: str = Field(
        ...,
        description="Name of the agent.",
        examples=["Example Agent"]
    )
    icon_link: str | None = Field(
        None,
        description="Link to the agent's icon or avatar, if available.",
        examples=["https://example.com/icon.png"]
    )
    tags: List[str] = Field(
        default_factory=list,
        description="List of tags associated with the agent.",
        examples=[["cool", "good"]]
    )
    description: str = Field(
        ...,
        description="Description of the agent, if available.",
        examples=["This is an example agent."]
    )
    prompt: str = Field(
        ...,
        description="Prompt or instructions for the agent.",
        examples=["This is an example prompt for the agent."]
    )
    output_schema: dict = Field(
        ...,
        description="Output schema for the agent's responses.",
        examples=[{
            "go": "string",
            "stop": "string",
        }]
    )
    



class AgentDetail(BaseModel):
    agent_id: str = Field(
        ...,
        description="Unique identifier of the agent.",
        examples=["agent-123"]
    )
    author_name: str | None = Field(
        ...,
        description="Name of the author of the agent.",
        examples=["Author Name"]
    )
    name: str = Field(
        ...,
        description="Name of the agent.",
        examples=["Example Agent"]
    )
    description: str = Field(
        ...,
        description="Description of the agent, if available.",
        examples=["This is an example agent."]
    )
    icon_link: str | None = Field(
        None,
        description="Link to the agent's icon or avatar, if available.",
        examples=["https://example.com/icon.png"]
    )
    tags: List[str] = Field(
        default_factory=list,
        description="List of tags associated with the agent.",
        examples=[["cool", "good"]]
    )
    prompt: str | None = Field(
        None,
        description="Prompt or instructions for the agent, if available.",
        examples=["This is an example prompt for the agent."]
    )
    created_at: str = Field(
        ...,
        description="Timestamp when the agent was created.",
        examples=["2023-10-01T12:00:00Z"]
    )
    updated_at: str = Field(
        ...,
        description="Timestamp when the agent was last updated.",
        examples=["2023-10-01T12:00:00Z"]
    )

