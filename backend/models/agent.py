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
    department_name: t.DepartmentsLiteral = Field(
        ...,
        description="Department to which the agent belongs.",
        examples=["Engineering", "Marketing"]
    )
    name: str = Field(
        ...,
        description="Username of the user.",
        examples=["example_user"]
    )
    description: str = Field(
        ...,
        description="Description of the agent, if available.",
        examples=["This is an example agent."]
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
    def mock(cls, type: t.DepartmentsLiteral) -> "Agent":
        match type:
            case "Common":
                return cls(
                    agent_id="agent-123",
                    agent_version=1,
                    department_name="Common",
                    description="This is a marketing agent.",
                    name="Common Agent",
                    tags=["common", "ai"],
                    icon_link="https://example.com/common_icon.png",
                    created_at=dt.datetime.now(),
                    updated_at=dt.datetime.now()
                )
            case "HR":
                return cls(
                    agent_id="agent-456",
                    agent_version=1,
                    department_name="HR",
                    description="This is a marketing agent.",
                    name="HR Agent",
                    tags=["hr", "ai"],
                    icon_link="https://example.com/hr_icon.png",
                    created_at=dt.datetime.now(),
                    updated_at=dt.datetime.now()
                )
            case "Sales":
                return cls(
                    agent_id="agent-456",
                    agent_version=1,
                    department_name="Sales",
                    description="This is a marketing agent.",
                    name="Sales Agent",
                    tags=["sales", "ai"],
                    icon_link="https://example.com/sales_icon.png",
                    created_at=dt.datetime.now(),
                    updated_at=dt.datetime.now()
                )
            case "Marketing":
                return cls(
                    agent_id="agent-789",
                    agent_version=1,
                    department_name="Marketing",
                    description="This is a marketing agent.",
                    name="Marketing Agent",
                    tags=["marketing", "ai"],
                    icon_link="https://example.com/marketing_icon.png",
                    created_at=dt.datetime.now(),
                    updated_at=dt.datetime.now()
                )
            case "CustomerSupport":
                return cls(
                    agent_id="agent-101",
                    agent_version=1,
                    department_name="CustomerSupport",
                    description="This is a marketing agent.",
                    name="Customer Support Agent",
                    tags=["support", "ai"],
                    icon_link="https://example.com/support_icon.png",
                    created_at=dt.datetime.now(),
                    updated_at=dt.datetime.now()
                )
            case "Finance":
                return cls(
                    agent_id="agent-102",
                    agent_version=1,
                    department_name="Finance",
                    description="This is a marketing agent.",
                    name="Finance Agent",
                    tags=["finance", "ai"],
                    icon_link="https://example.com/finance_icon.png",
                    created_at=dt.datetime.now(),
                    updated_at=dt.datetime.now()
                )
            case "Planning":
                return cls(
                    agent_id="agent-103",
                    agent_version=1,
                    department_name="Planning",
                    description="This is a marketing agent.",
                    name="Planning Agent",
                    tags=["planning", "ai"],
                    icon_link="https://example.com/planning_icon.png",
                    created_at=dt.datetime.now(),
                    updated_at=dt.datetime.now()
                )
            case "BusinessSupport":
                return cls(
                    agent_id="agent-104",
                    agent_version=1,
                    department_name="BusinessSupport",
                    description="This is a marketing agent.",
                    name="Business Support Agent",
                    tags=["business", "ai"],
                    icon_link="https://example.com/business_icon.png",
                    created_at=dt.datetime.now(),
                    updated_at=dt.datetime.now()
                )
            case "ProductDevelopment":
                return cls(
                    agent_id="agent-105",
                    agent_version=1,
                    department_name="ProductDevelopment",
                    description="This is a marketing agent.",
                    name="Product Development Agent",
                    tags=["product", "ai"],
                    icon_link="https://example.com/product_icon.png",
                    created_at=dt.datetime.now(),
                    updated_at=dt.datetime.now()
                )
            case "InternationalSales":
                return cls(
                    agent_id="agent-106",
                    agent_version=1,
                    department_name="InternationalSales",
                    description="This is a marketing agent.",
                    name="International Sales Agent",
                    tags=["international", "sales", "ai"],
                    icon_link="https://example.com/international_sales_icon.png",
                    created_at=dt.datetime.now(),
                    updated_at=dt.datetime.now()
                )


class AgentDetail(Agent):
    author_name: str | None = Field(
        None,
        description="Name of the author of the agent.",
        examples=["Author Name"]
    )
    prompt: str | None = Field(
        None,
        description="Prompt or instructions for the agent, if available.",
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
    def failed(cls) -> "AgentDetail":
        return cls(
            agent_id="",
            agent_version=0,
            department_name="Common",
            name="",
            tags=[],
            icon_link=None,
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now(),
            author_name="",
            description="",
            prompt="",
            output_schema=None
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
        examples=[[Agent.mock(type="HR")]]
    )

    @classmethod
    def mocks(cls) -> List["AgentRecommendation"]:
        return [
            cls(
                department_name="Common",
                agents=[Agent.mock(type="Common")]
            ),
            cls(
                department_name="HR",
                agents=[Agent.mock(type="HR")]
            ),
            cls(
                department_name="Sales",
                agents=[Agent.mock(type="Sales")]
            ),
            cls(
                department_name="Marketing",
                agents=[Agent.mock(type="Marketing")]
            ),
            cls(
                department_name="CustomerSupport",
                agents=[Agent.mock(type="CustomerSupport")]
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
    department_name: t.DepartmentsLiteral = Field(
        ...,
        description="Department to which the agent belongs.",
        examples=["BusinessSupport", "ProductDevelopment", "InternationalSales"]
    )

    @classmethod
    def mock(cls) -> "AgentMarketPlace":
        return cls(
            agent_id="agent-123",
            agent_version=1,
            name="Example Agent",
            tags=["cool", "good"],
            icon_link="https://example.com/icon.png",
            department_name="BusinessSupport"
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
    department_name: t.DepartmentsLiteral = Field(
        ...,
        description="Name of the department to which the agent belongs.",
        examples=["Engineering", "Marketing"]
    )
    output_schema: List[Attribute] | None = Field(
        None,
        description="Output schema for the agent's responses. if not provided, it will be raw string",
        examples=[[
            Attribute(attribute="field1", type="str"),
            Attribute(attribute="field2", type="int")
        ]]
    )

    @classmethod
    def mock(cls) -> "AgentPublish":
        return AgentPublish(
            agent_id="agent-123",
            name="Example Agent",
            icon_link="https://example.com/icon.png",
            tags=["cool", "good"],
            description="This is an example agent.",
            prompt="This is an example prompt for the agent.",
            department_name="CustomerSupport",
            output_schema=[
                Attribute(attribute="field1", type="str"),
                Attribute(attribute="field2", type="int")
            ]
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