import datetime as dt
import uuid

from pydantic import BaseModel, Field

from backend.models.agent import Agent


class RecommendationMaster(BaseModel):
    
    recommendation_id: str = Field(
        ..., 
        description="A unique identifier for the recommendation.",
        examples=[str(uuid.uuid4())]
    )
    title: str = Field(
        ..., 
        description="Title of the recommendation, unique across all recommendations.",
        examples=["New Launching Festival"]
    )
    description: str = Field(
        ...,
        description="A brief description of the recommendation's content.",
        examples=["A festival to celebrate the launch of new products."]
    )
    created_at: dt.datetime = Field(
        default_factory=dt.datetime.now,
        description="The date and time when the recommendation was created.",
        examples=[dt.datetime.now()]
    )
    updated_at: dt.datetime = Field(
        default_factory=dt.datetime.now,
        description="The date and time when the recommendation was last updated.",
        examples=[dt.datetime.now()]
    )
    departments: list[str] = Field(
        default_factory=list,
        description="List of departments associated with the recommendation.",
        examples=[["Marketing", "Sales"]]
    )


class Recommendation(BaseModel):
    
    recommendation_id: str = Field(
        ..., 
        description="A unique identifier for the recommendation.",
        examples=[str(uuid.uuid4())]
    )
    work_when: dt.datetime = Field(
        ...,
        description="The date and time when the recommendation is intended to be worked on.",
        examples=[dt.datetime.now()]
    )
    work_where: str = Field(
        ...,
        description="The location where the recommendation is intended to be worked on.",
        examples=["Head Office"]
    )
    work_whom: str = Field(
        ...,
        description="The person or team with whom the recommendation is intended to be worked on.",
        examples=["John Doe"]
    )
    work_details: str = Field(
        ...,
        description="Detailed information about the work associated with the recommendation.",
        examples=["Details about the work to be done."]
    )
    agents: list[Agent] = Field(
        default_factory=list,
        description="List of agents associated with the recommendation.",
        examples=[
            [
                Agent(
                    agent_id="agent1", name="Agent One", agent_version=1, icon_link="https://example.com/icon1.png", department_name="Engineering"
                ),
                Agent(
                    agent_id="agent2", name="Agent Two", agent_version=2, icon_link="https://example.com/icon2.png", department_name="Marketing"
                )
            ]
        ]
    )
    