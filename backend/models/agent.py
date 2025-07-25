import datetime as dt
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

import backend._types as t

class Attribute(BaseModel):
    """
    Represents an attribute for the output schema of an agent's response.
    """
    attribute: str = Field(
        ...,
        description="attribute for the output schema",
        examples=["field1", "field2"]
    )
    type: str = Field(
        ...,
        description="type of the output schema, e.g., 'str', 'int', 'float', 'bool'.",
        examples=['str', 'int', 'float', 'bool']
    )


class Agent(BaseModel):
    agent_id: str = Field(
        ...,
        description="Unique identifier of the model.",
        examples=["user-123"]
    )
    agent_version: int = Field(
        ...,
        description="Version of the agent.",
        examples=[1]
    )
    department_name: str = Field(
        ...,
        description="Department to which the agent belongs.",
        examples=["Engineering", "Marketing"]
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
    department_id: str | None = Field(
        None,
        description="ID of the department to which the agent belongs, if applicable.",
        examples=["department-123"]
    )

    @classmethod
    def mock(cls, type: t.DepartmentsLiteral) -> "Agent":
        match type:
            case "Engineering":
                return cls(
                    agent_id="agent-123",
                    agent_version=1,
                    department_name="Engineering",
                    name="Engineering Agent",
                    tags=["engineering", "ai"],
                    icon_link="https://example.com/engineering_icon.png",
                    department_id="engineering-123"
                )
            case "Design":
                return cls(
                    agent_id="agent-456",
                    agent_version=1,
                    department_name="Design",
                    name="Design Agent",
                    tags=["design", "ai"],
                    icon_link="https://example.com/design_icon.png",
                    department_id="design-456"
                )
            case "Marketing":
                return cls(
                    agent_id="agent-456",
                    agent_version=1,
                    department_name="Marketing",
                    name="Marketing Agent",
                    tags=["marketing", "ai"],
                    icon_link="https://example.com/marketing_icon.png",
                    department_id="marketing-456"
                )
            case "Sales":
                return cls(
                    agent_id="agent-789",
                    agent_version=1,
                    department_name="Sales",
                    name="Sales Agent",
                    tags=["sales", "ai"],
                    icon_link="https://example.com/sales_icon.png",
                    department_id="sales-789"
                )
            case "Support":
                return cls(
                    agent_id="agent-101",
                    agent_version=1,
                    department_name="Support",
                    name="Support Agent",
                    tags=["support", "ai"],
                    icon_link="https://example.com/support_icon.png",
                    department_id="support-101"
                )

class AgentRequest(BaseModel):
    agent_id: str = Field(
        ...,
        description="Unique identifier of the agent.",
        examples=["agent-123"]
    )
    agent_version: int = Field(
        ...,
        description="Version of the agent.",
        examples=[1]
    )
    department_id: str | None = Field(
        None,
        description="ID of the department to which the agent belongs, if applicable.",
        examples=["department-123"]
    )

    @classmethod
    def mock(cls) -> "AgentRequest":
        return cls(
            agent_id="agent-123",
            agent_version=1,
            department_id="department-123"
        )

class AgentRecommendation(BaseModel):
    department_name: t.DepartmentsLiteral = Field(
        ...,
        description="Name of the department to which the agent belongs.",
    )
    agents: List[Agent] = Field(
        default_factory=list,
        description="List of agents associated with the recommendation.",
        examples=[[Agent.mock(type="Engineering")]]
    )

    @classmethod
    def mocks(cls) -> List["AgentRecommendation"]:
        return [
            cls(
                department_name="Engineering",
                agents=[Agent.mock(type="Engineering")]
            ),
            cls(
                department_name="Design",
                agents=[Agent.mock(type="Design")]
            ),
            cls(
                department_name="Marketing",
                agents=[Agent.mock(type="Marketing")]
            ),
            cls(
                department_name="Sales",
                agents=[Agent.mock(type="Sales")]
            ),
            cls(
                department_name="Support",
                agents=[Agent.mock(type="Support")]
            )
            
        ]


class AgentMarketPlace(BaseModel):
    agent_id: str = Field(
        ...,
        description="Unique identifier of the model.",
        examples=["user-123"]
    )
    agent_version: int = Field(
        ...,
        description="Version of the agent.",
        examples=[1]
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
    subscribed: bool = Field(
        default=False,
        description="Indicates whether the user is subscribed to this agent.",
        examples=[True, False]
    )

class AgentPublish(BaseModel):

    agent_id: str | None = Field(
        None,
        description="Unique identifier of the agent. If not provided, a new ID will be generated.",
        examples=["agent-123"]
    )
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
    output_schema: List[Attribute] | None = Field(
        None,
        description="Output schema for the agent's responses. if not provided, it will be raw string",
        examples=[[
            Attribute(attribute="field1", type="str"),
            Attribute(attribute="field2", type="int")
        ]]
    )
    



class AgentDetail(BaseModel):
    agent_id: str = Field(
        ...,
        description="Unique identifier of the agent.",
        examples=["agent-123"]
    )
    agent_version: int = Field(
        ...,
        description="Version of the agent.",
        examples=[1]
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
    created_at: dt.datetime = Field(
        ...,
        description="Timestamp when the agent was created.",
        examples=[dt.datetime.now()]
    )
    updated_at: dt.datetime = Field(
        ...,
        description="Timestamp when the agent was last updated.",
        examples=[dt.datetime.now()]
    )

    @classmethod
    def failed(cls) -> "AgentDetail":
        return cls(
            agent_id="",
            agent_version=0,
            author_name=None,
            name="",
            description="",
            icon_link=None,
            tags=[],
            prompt=None,
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now()
        )


class AgentSpec(BaseModel):
    """
    Represents the specification of an agent, including its details and output schema.
    """
    model_config= ConfigDict(from_attributes=True)
    agent_id: str = Field(
        ...,
        description="Unique identifier of the agent.",
        examples=["agent-123"]
    )
    version: int = Field(
        ...,
        description="Version of the agent specification.",
        examples=[1]
    )
    prompt: str = Field(
        ...,
        description="Prompt or instructions for the agent.",
        examples=["This is an example prompt for the agent."]
    )
    output_schema: List[Attribute] | None = Field(
        default=None,
        description="Output schema for the agent's responses.",
        examples=[[
            Attribute(attribute="field1", type="str"),
            Attribute(attribute="field2", type="int")
        ]]
    )

    

    @classmethod
    def failed(cls) -> "AgentSpec":
        return cls(
            agent_id="",
            version=0,
            prompt="",
            output_schema=None
        )