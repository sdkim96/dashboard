import datetime as dt
import uuid
from typing import List

from pydantic import BaseModel, Field

from backend.models.agent import Agent, AgentRecommendation


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

    @classmethod
    def mock(cls) -> "RecommendationMaster":
        return cls(
            recommendation_id=str(uuid.uuid4()),
            title="New Launching Festival",
            description="A festival to celebrate the launch of new products.",
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now(),
            departments=["Engineering", "Design"]
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
    agents: List[AgentRecommendation] = Field(
        default_factory=list,
        description="List of agents associated with the recommendation.",
        examples=[
            AgentRecommendation.mocks()
        ]
    )

    @classmethod
    def failed(cls) -> "Recommendation":
        return cls(
            recommendation_id="",
            work_when=dt.datetime.now(),
            work_where="",
            work_whom="",
            work_details="",
            agents=[]
        )

    @classmethod
    def mock(cls) -> "Recommendation":
        return cls(
            recommendation_id=str(uuid.uuid4()),
            work_when=dt.datetime.now(),
            work_where="Head Office",
            work_whom="John Doe",
            work_details="Details about the work to be done.",
            agents=AgentRecommendation.mocks()
        )
    