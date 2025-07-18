from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

import backend.constants as c
import backend.deps as dp
import backend.models.api as mdl
import backend.services.agents as svc

AGENTS = APIRouter(
    prefix=c.APIPrefix.AGENTS.value,
    tags=[c.APITag.AGENTS],
)

@AGENTS.get(
    path="",
    summary="Explore Agents in Marketplace",
    description="""
## Explore Agents in Marketplace

This api lets user explore agents available in the marketplace.
It supports pagination and searching by agent name or tags.

""",
    response_model=mdl.GetAvailableAgentsResponse,
)
def get_available_agents(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    params: mdl.GetAvailableAgentsRequest = Depends(),
) -> mdl.GetAvailableAgentsResponse:
    """
    Explores agents available in the marketplace.
    
    Args:
        
        
    Returns:
        GetAvailableAgentsResponse: Response model containing a list of available agents in marketplace.
    """
    agents, err = svc.get_available_agents(
        session=session,
        request_id=request_id,
        username=user_profile.username,
        offset=params.offset,
        limit=params.size,
        search=params.search,
    )
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agents: {err}"
        )

    return mdl.GetAvailableAgentsResponse(
        status="success",
        message="Available agents retrieved successfully.",
        request_id=request_id,
        agents=agents,
        total=len(agents),
        page=params.page,
        size=params.size,
        has_next=len(agents) > params.offset + params.size,
    )

@AGENTS.get(
    path="/{agent_id}",
    summary="Get Agent Details",
    description="Retrieves details of a specific agent by its ID.",
    response_model=mdl.GetAgentResponse,
)
def get_agent(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    agent_id: str,
) -> mdl.GetAgentResponse:
    """ Retrieves details of a specific agent by its ID.
    
    Args:
        agent_id (str): Unique identifier of the agent.
        
    Returns:
        GetAgentResponse: Response model containing agent details.
    """
    agent_detail, err = svc.get_detail_by_agent_id(
        session=session,
        request_id=request_id,
        username=user_profile.username,
        agent_id=agent_id,
    )
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agent details."
        )
    
    return mdl.GetAgentResponse(
        status="success",
        message="Agent details retrieved successfully.",
        request_id=request_id,
        agent=agent_detail
    )

@AGENTS.post(
    path="/{agent_id}/subscribe",
    summary="Subscribe to Agent",
    description="Subscribes to an agent by its ID.",
    response_model=mdl.PostSubscribeAgentResponse,
)
async def subscribe_agent(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    agent_id: str,
) -> mdl.PostSubscribeAgentResponse:
    """
    Subscribes to an agent by its ID.
    
    Args:
        agent_id (str): Unique identifier of the agent to subscribe to.
        
    Returns:
        PostSubscribeAgentResponse: Response model indicating the result of the subscription.
    """
    
    return mdl.PostSubscribeAgentResponse(
        status="success",
        message="Agent subscribed successfully.",
        request_id=request_id,
    )



@AGENTS.post(
    path="/publish",
    summary="Publish Agent",
    description="Publishes a new agent to the marketplace.",
    response_model=mdl.PostPublishAgentResponse,
)
async def publish_agent(
    session: Annotated[Session, Depends(dp.get_db)],
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    body: mdl.PostPublishAgentRequest,
) -> mdl.PostPublishAgentResponse:
    """
    Publishes a new agent to the marketplace.

    Args:
        body (PostPublishAgentRequest): Request body containing agent details to publish.
        
    Returns:
        PostPublishAgentResponse: Response model indicating the result of the publication.
    """
    publish = body.agent
    ok, err = svc.publish_agent(
        session=session,
        publish=publish,
        user_profile=user_profile,
        request_id=request_id,
    )
    if err or not ok:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving agents: {err}"
        )
    
    return mdl.PostPublishAgentResponse(
        status="success",
        message="Agent subscribed successfully.",
        request_id=request_id,
    )


@AGENTS.put(
    path="/{agent_id}",
    summary="Modify Agent",
    description="Modifies a new agent to the marketplace.",
    response_model=mdl.PutModifyAgentResponse,
)
async def modify_agent(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    agent_id: str,
    body: mdl.PutModifyAgentRequest,
) -> mdl.PutModifyAgentResponse:
    """
    Subscribes to an agent by its ID.
    
    Args:
        body (ModifyAgentRequest): Request body containing agent details to modify.
        
    Returns:
        PutModifyAgentResponse: Response model indicating the result of the modification.
    """
    
    return mdl.PutModifyAgentResponse(
        status="success",
        message="Agent subscribed successfully.",
        request_id=request_id,
        
    )