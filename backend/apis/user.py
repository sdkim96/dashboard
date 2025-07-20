from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import backend.constants as c
import backend.deps as dp
import backend.models.api as mdl

import backend.services.user as svc

USER = APIRouter(
    prefix=c.APIPrefix.USER.value,
    tags=[c.APITag.USER],
)

@USER.get(
    path="",
    summary="Get User Information",
    description="Retrieves information about the current user.",
    response_model=mdl.GetMeResponse,
)
def get_me(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> mdl.GetMeResponse:
    """
    Retrieves the current user's information.
    
    Args:
        request_id (str): Unique identifier for the request.
        session (Session): Database session for querying user data.
        user_profile (mdl.User): Current user's profile information.
        
    Returns:
        GetMeResponse: User information model.
    """
    agents, llms, err = svc.get_me(
        session=session,
        user_profile=user_profile,
        request_id=request_id,
    )
    if err:
        return mdl.GetMeResponse(
            status="error",
            message="Failed to retrieve conversations.",
            request_id=request_id,
            user=user_profile,
            agents=agents,
            llms=llms
        )
    return mdl.GetMeResponse(
        status="success",
        message="User information retrieved successfully.",
        request_id=request_id,
        user=user_profile,
        agents=agents,
        llms=llms
    )

    # return mdl.GetMeResponse(
    #     status="success",
    #     message="Conversations retrieved successfully.",
    #     request_id=request_id,
    #     conversations=conversations
    # )
    # return mdl.GetMeResponse(
    #     status="success",
    #     message="User information retrieved successfully.",
    #     request_id=request_id,
    #     user=mdl.User(
    #         user_id="user-123",
    #         username="example_user",
    #         email="",
    #         icon_link="https://example.com/icon.png",
    #         is_superuser=False,
    #     ),
    #     agents=[
    #         mdl.Agent(
    #             agent_id="agent-123", 
    #             name="Example Agent", 
    #             icon_link=None, 
    #             tags=["cool", "good"],
    #             agent_version=1,
    #         )
    #     ],
    #     models=[
    #         mdl.LLMModel(
    #             issuer="openai",
    #             name="Example Model",
    #             description="An example LLM model.",
    #             deployment_id="deployment-123",
    #             icon_link=None
    #         )
    #     ]
    # )
    
