from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

import backend.constants as c
import backend.deps as dp
import backend.models.api as mdl

AGENTS = APIRouter(
    prefix=c.APIPrefix.AGENTS.value,
    tags=[c.APITag.AGENTS],
)

@AGENTS.get(
    path="",
    summary="Explore Agents in Marketplace",
    description="Explores agents available in the marketplace.",
    response_model=mdl.GetAvailableAgentsResponse,
)
async def get_available_agents(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
) -> mdl.GetAvailableAgentsResponse:
    """
    Explores agents available in the marketplace.
    
    Args:
        
        
    Returns:
        StreamingResponse: A streaming response containing the generated completion.
    """
    
    
    return mdl.GetAvailableAgentsResponse(
        status="success",
        message="Available agents retrieved successfully.",
        request_id=request_id,
        agents=[
            mdl.Agent(
                agent_id="agent-123",
                name="Example Agent",
                icon_link=None,
            )
        ]
    )

@AGENTS.get(
    path="/{agent_id}",
    summary="Get Agent Details",
    description="Retrieves details of a specific agent by its ID.",
    response_model=mdl.GetAgentResponse,
)
async def get_agent(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    agent_id: str,
) -> mdl.GetAgentResponse:
    """
    Retrieves details of a specific agent by its ID.
    
    Args:
        agent_id (str): Unique identifier of the agent.
        
    Returns:
        GetAgentResponse: Response model containing agent details.
    """
    
    return mdl.GetAgentResponse(
        status="success",
        message="Agent details retrieved successfully.",
        request_id=request_id,
        agent=mdl.AgentDetail(
            agent_id=agent_id,
            name="Example Agent",
            icon_link=None,
            tags=["cool", "good"],
            description="This is an example agent used for demonstration purposes.",
            author_name="Author Name",
            prompt="This is an example prompt for the agent.",
            created_at="2023-10-01T12:00:00Z",
            updated_at="2023-10-01T12:00:00Z"
        )
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
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    body: mdl.PostPublishAgentRequest,
) -> mdl.PostPublishAgentResponse:
    """
    Subscribes to an agent by its ID.
    
    Args:
        body (PostPublishAgentRequest): Request body containing agent details to publish.
        
    Returns:
        PostPublishAgentResponse: Response model indicating the result of the subscription.
    """
    
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