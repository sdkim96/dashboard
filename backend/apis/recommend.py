import datetime as dt
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

import backend.constants as c
import backend.deps as dp
import backend.models as mdl
import backend.services.conversations as svc

RECOMMENDATIONS = APIRouter(
    prefix=c.APIPrefix.RECOMMENDATIONS.value,
    tags=[c.APITag.RECOMMENDATIONS],
)

@RECOMMENDATIONS.get("", response_model=list[mdl.RecommendationMaster], summary="Get Recommendations")
def get_recommendations(
    db: Annotated[Session, Depends(dp.get_db)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> list[mdl.RecommendationMaster]:
    """
    Get a list of recommended tools for the user.

    Args:
        db (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.

    Returns:
        list[mdl.Recommendation]: A list of recommended tools.
    """


@RECOMMENDATIONS.get("/{recommendation_id}", response_model=mdl.Recommendation, summary="Get Recommendation by ID")
def get_recommendation_by_id(
    db: Annotated[Session, Depends(dp.get_db)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> mdl.Recommendation:
    """
    Get a list of recommended tools for the user.

    Args:
        db (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.

    Returns:
        list[mdl.Recommendation]: A list of recommended tools.
    """

@RECOMMENDATIONS.post("", response_model=mdl.Recommendation, summary="Create Recommendation")
async def create_recommendation(
    db: Annotated[Session, Depends(dp.get_db)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> mdl.Recommendation:
    """
    Create a new recommendation for the user.

    Args:
        db (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.

    Returns:
        mdl.Recommendation: The created recommendation.
    """
    # Implementation for creating a recommendation goes here
    pass


@RECOMMENDATIONS.post("/{agent_id}/completion", response_model=mdl.Recommendation, summary="Update Recommendation")
async def chat_completion_with_agent():
    """
    Update a recommendation with the agent's response.

    Args:
        db (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.

    Returns:
        mdl.Recommendation: The updated recommendation.
    """
    # Implementation for updating a recommendation goes here
    pass
    

@RECOMMENDATIONS.get("/{agent_id}/conversation", response_model=List[mdl.RecommendationMessage], summary="Get Recommendation Conversation")
def get_recommendation_conversation(
    db: Annotated[Session, Depends(dp.get_db)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> List[mdl.RecommendationMessage]:
    """
    Get the conversation associated with a recommendation.

    Args:
        db (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.

    Returns:
        List[mdl.RecommendationMessage]: A list of messages in the conversation.
    """
    # Implementation for getting recommendation conversation goes here
    pass

    Returns:
        mdl.Recommendation: The recommendation with its conversation.
    """
    # Implementation for getting recommendation conversation goes here
    pass