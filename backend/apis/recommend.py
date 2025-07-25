import datetime as dt
import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

import backend.constants as c
import backend.deps as dp
import backend.models as mdl
import backend.services.conversations as svc

RECOMMENDATIONS = APIRouter(
    prefix=c.APIPrefix.RECOMMENDATIONS.value,
    tags=[c.APITag.RECOMMENDATIONS],
)

@RECOMMENDATIONS.get(
    path="", 
    summary="Get Recommendations",
    description=""" 
## Retrieve a list of recommendations for the user.

This endpoint fetches a list of recommendations tailored for the user 
based on their profile and preferences. 
It returns a list of `RecommendationMaster` objects, each containing details about the recommendation such as title, description, creation date, and associated departments.

""",
    response_model=mdl.GetRecommendationsResponse, 
    
)
def get_recommendations(
    db: Annotated[Session, Depends(dp.get_db)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> mdl.GetRecommendationsResponse:
    """
    Get a list of recommended tools for the user.

    Args:
        db (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.

    Returns:
        list[mdl.Recommendation]: A list of recommended tools.
    """
    return mdl.GetRecommendationsResponse.mock()


@RECOMMENDATIONS.get(
    path="/{recommendation_id}", 
    summary="Get Recommendation by ID",
    description=""" 
## Retrieve a specific recommendation by its ID.

This endpoint fetches a recommendation based on the provided `recommendation_id`.
It returns a `Recommendation` object containing details about the recommendation such as title, description, creation

""",
    response_model=mdl.GetRecommendationByIDResponse
)
def get_recommendation_by_id(
    db: Annotated[Session, Depends(dp.get_db)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    recommendation_id: str,
) -> mdl.GetRecommendationByIDResponse:
    """
    Get a list of recommended tools for the user.

    Args:
        db (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.

    Returns:
        list[mdl.Recommendation]: A list of recommended tools.
    """
    mock = mdl.GetRecommendationByIDResponse.mock()
    return mock


@RECOMMENDATIONS.post(
    path="", 
    summary="Create Recommendation",
    description=""" 
## Create a new recommendation.

This endpoint allows users to create a new recommendation by providing the necessary details.
It returns the created `Recommendation` object.

""",
    response_model=mdl.PostRecommendationResponse
)
async def create_recommendation(
    db: Annotated[Session, Depends(dp.get_db)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    body: mdl.PostRescommendationRequest
) -> mdl.PostRecommendationResponse:
    """
    Create a new recommendation for the user.

    Args:
        db (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.

    Returns:
        mdl.Recommendation: The created recommendation.
    """
    return mdl.PostRecommendationResponse.mock()


@RECOMMENDATIONS.post(
    path="/{agent_id}/completion", 
    summary="Chat With Recommended Agent",
    description=""" 
## Interact with an agent to create a recommendation.
 
This endpoint allows users to interact with a specific agent to create a recommendation.
It streams the response back as a `StreamingResponse` object, allowing for real-time updates during the interaction.
The agent's ID is provided in the URL path, and the request body contains the necessary details for the interaction.

""",
    response_class=StreamingResponse
)
async def chat_completion_with_agent(
    db: Annotated[Session, Depends(dp.get_db)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    agent_id: str,
    body: mdl.PostRecommendationCompletionRequest
):
    """
    Create a new recommendation by interacting with an agent.
    """
    # Implementation for updating a recommendation goes here
    pass
    

@RECOMMENDATIONS.get(
    path="/{agent_id}/conversation",
    summary="Get Recommended Agent's Conversation",
        description=""" 
## Retrieve the conversation associated with a recommendation.

This endpoint fetches the conversation associated with a specific recommendation.
It returns a list of `RecommendationMessage` objects, each containing details about the message such as content, sender, and timestamp.
The `agent_id` is provided in the URL path to identify
""",
    response_model=mdl.GetRecommendationConversationResponse
)
def get_recommendation_conversation(
    db: Annotated[Session, Depends(dp.get_db)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    agent_id: str,
) -> mdl.GetRecommendationConversationResponse:
    """
    Get the conversation associated with a recommendation.

    Args:
        db (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.

    Returns:
        List[mdl.RecommendationMessage]: A list of messages in the conversation.
    """
    return mdl.GetRecommendationConversationResponse.mock()