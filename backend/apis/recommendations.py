import datetime as dt
import uuid
from typing import Annotated, List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

import backend.constants as c
import backend.deps as dp
import backend.models as mdl

import backend.services.conversations as csvc
import backend.services.recommendations as svc

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
    request_id: Annotated[str, Depends(dp.generate_request_id)],
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
    recommendations, err = svc.get_recommendation_masters(
        session=session,
        user_profile=user_profile
    )
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve recommendations: {err}"
        )

    return mdl.GetRecommendationsResponse(
        request_id=request_id,
        recommendations=recommendations,
        total=len(recommendations),
        page=1,
        size=len(recommendations),
        has_next=False,
    )


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
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    request_id: Annotated[str, Depends(dp.generate_request_id)],
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
    recommendation, err = svc.get_recommendation_by_id(
        session=session,
        user_profile=user_profile,
        recommendation_id=recommendation_id
    )
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve recommendation: {err}"
        )

    return mdl.GetRecommendationByIDResponse(
        request_id=request_id,
        recommendation=recommendation
    )


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
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    body: mdl.PostRescommendationRequest
) -> mdl.PostRecommendationResponse:
    """
    Create a new recommendation for the user.

    Args:
        session (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.

    Returns:
        mdl.Recommendation: The created recommendation.
    """
    recommendation, err = await svc.create_recommendation(
        session=session,
        user_profile=user_profile,
        body=body,
        request_id=request_id
    )
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create recommendation: {err}"
        )

    return mdl.PostRecommendationResponse(
        request_id=request_id,
        recommendation=recommendation
    )


@RECOMMENDATIONS.post(
    path="/{recommendation_id}/completion", 
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
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    recommendation_id: str,
    body: mdl.PostRecommendationCompletionRequest
) -> StreamingResponse:
    """
    Create a new recommendation by interacting with an agent.
    """
    if recommendation_id is None or recommendation_id == "":
        raise HTTPException(
            status_code=400,
            detail="Recommendation ID is required."
        )
    
    generator = svc.chat_completion_with_agent(
        session=session,
        request_id=request_id,
        user_profile=user_profile,
        body=body,
        recommendation_id=recommendation_id
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
    )


@RECOMMENDATIONS.get(
    path="/{recommendation_id}/conversations", 
    summary="Get Recommendation Conversations",
    description=""" 
## Interact with an agent to create a recommendation.
 
This endpoint allows users to interact with a specific agent to create a recommendation.
It streams the response back as a `StreamingResponse` object, allowing for real-time updates during the interaction.
The agent's ID is provided in the URL path, and the request body contains the necessary details for the interaction.

""",
    response_model=mdl.GetConversationResponse
)
async def get_conversation_by_recommendation(
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    recommendation_id: str,
    params: mdl.GetConversationByRecommendationRequest = Depends()
) -> mdl.GetConversationResponse:
    """
    Create a new recommendation by interacting with an agent.
    """

    conversation_id, err = svc.get_conversation_id_by_recommendation(
        session=session,
        request_id=request_id,
        user_profile=user_profile,
        recommendation_id=recommendation_id,
        params=params
    )
    if err or conversation_id == "":
        return mdl.GetConversationResponse(
            status="error",
            message="No conversation. Call /api/v1/conversation/new first.",
            request_id=request_id,
            conversation=mdl.ConversationMaster.failed(),
            messages=[]
        )
    conversation, err = csvc.get_conversation_by_id(
        session=session,
        user_profile=user_profile,
        request_id=request_id,
        conversation_id=conversation_id,
        conversation_type="recommendation"
    )
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve conversation: {err}"
        )
        
    messages, err = csvc.get_messages(
        session=session,
        user_profile=user_profile,
        request_id=request_id,
        conversation_id=conversation_id
    )
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve messages for the conversation: {err}"
        )
    
    return mdl.GetConversationResponse(
        status="success",
        message="Conversation details retrieved successfully.",
        request_id=request_id,
        conversation=conversation,
        messages=messages
    )


