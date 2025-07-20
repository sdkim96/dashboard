from typing import Annotated
from fastapi import APIRouter, Depends

import backend.constants as c
import backend.deps as dp
import backend.models.api as mdl

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
) -> mdl.GetMeResponse:
    """
    Retrieves the current user's information.
    
    Args:
        request_id (str): Unique identifier for the request.
        
    Returns:
        GetMeResponse: User information model.
    """
    return mdl.GetMeResponse(
        status="success",
        message="User information retrieved successfully.",
        request_id=request_id,
        user=mdl.User(
            user_id="user-123",
            username="example_user",
            email="",
            icon_link="https://example.com/icon.png",
            is_superuser=False,
        ),
        agents=[
            mdl.Agent(
                agent_id="agent-123", 
                name="Example Agent", 
                icon_link=None, 
                tags=["cool", "good"],
                agent_version=1,
            )
        ],
        models=[
            mdl.LLMModel(
                issuer="openai",
                name="Example Model",
                description="An example LLM model.",
                deployment_id="deployment-123",
                icon_link=None
            )
        ]
    )
    
