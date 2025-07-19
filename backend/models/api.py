import uuid
import datetime as dt
from typing import List

from pydantic import BaseModel, Field

import backend._types as t
import backend.constants as c

from backend.models.user import User
from backend.models.agent import Agent, AgentDetail, AgentPublish, Attribute
from backend.models.llm import LLMModel
from backend.models.conversations import ConversationMaster
from backend.models.message import MessageRequest, Message, Content

class BaseRequest(BaseModel):
    pass


class BaseResponse(BaseModel):
    """
    Base response model for API responses.
    """
    status: t.APIStatusLiteral = Field(
        default='success', 
        description="Status of the response, e.g., 'success' or 'error'.",
        examples=["success", "error"]
    )
    message: str = Field(
        default=c.API_BASE_MESSAGE, 
        description="Message providing additional information about the response.",
        examples=[c.API_BASE_MESSAGE]
    )
    request_id: str = Field(
        ...,
        description="Unique identifier for the request, used for tracking and debugging.",
        examples=[str(uuid.uuid4())]
    )
    
#######################
## 1. Request Models ##
#######################

class GetAvailableAgentsRequest(BaseRequest):
    """
    GET /api/v1/agents Request model
    """
    search: str | None = Field(
        default=None,
        description="Search term to filter agents by name or description.",
        examples=["example", "cool agent"]
    )
    page: int = Field(
        default=1,
        ge=1,
        description="Page number of the results to return.",
        examples=[1]
    )
    size: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Number of agents per page.",
        examples=[20]
    )

    @property
    def offset(self) -> int:
        """Offset to be used in DB queries"""
        return (self.page - 1) * self.size

class PostPublishAgentRequest(BaseRequest):
    """
    POST /api/v1/agent/publish Request model
    """
    agent: AgentPublish = Field(
        ...,
        description="Details of the agent to be published.",
        examples=[AgentPublish(
            agent_id=None,  # None for new agents, or provide existing agent ID for updates
            name="Example Agent", 
            icon_link=None,
            description="This is an example agent.",
            tags=["cool", "good"],
            prompt="This is an example prompt for the agent.",
            output_schema=[Attribute(
                attribute="field1",
                type="str"
            )]
        )]
    )


class PutModifyAgentRequest(BaseRequest):
    """
    POST /api/v1/agent/publish Request model
    """
    agent: AgentPublish = Field(
        ...,
        description="Details of the agent to be published.",
        examples=[AgentPublish(
            agent_id="agent-123",  # Existing agent ID for updates
            name="Example Agent", 
            icon_link=None,
            description="This is an example agent.",
            tags=["cool", "good"],
            prompt="This is an example prompt for the agent.",
            output_schema=[Attribute(
                attribute="field1",
                type="str"
            )]
        )]
    )


class PostGenerateCompletionRequest(BaseRequest):
    """
    POST /api/v1/completion Request model
    """
    action: t.CompletionActionLiteral = Field(
        ...,
        description="Action to be performed for the completion request, e.g., 'next', 'retry', or 'variant'.",
        examples=["next", "retry", "variant"]
    )
    conversation_id: str = Field(
        ...,
        description="ID of the conversation for which the completion is requested.",
        examples=[str(uuid.uuid4())]
    )
    parent_message_id: str | None = Field(
        ...,
        description="ID of the parent message for the completion request.",
        examples=[str(uuid.uuid4())]
    )
    agent_id: str = Field(
        ...,
        description="ID of the agent to use for generating the completion.",
        examples=["agent-123"]
    )
    agent_version: int = Field(
        default=0,
        ge=0,
        description="Version of the agent to use for generating the completion.",
        examples=[1]
    )
    model: str = Field(
        ...,
        description="Model to be used for generating the completion.",
        examples=["gpt-3.5-turbo"]
    )
    messages: List[MessageRequest] = Field(
        ...,
        description="List of messages in the conversation for which the completion is requested.",
        examples=[[MessageRequest(
            content=Content(type='text', parts=["Hello, how can I help you?"]),
        )]]
    )

########################
## 2. Response Models ##
########################
class GetMeResponse(BaseResponse):
    """
    GET /api/v1/user Response model
    """
    user: User = Field(
        ...,
        description="User information model containing details about the current user.",
        examples=[User(
            user_id=str(uuid.uuid4()),
            username="example_user",
            email="ss@gamil.com",
            icon_link="https://example.com/icon.png",
            is_superuser=False,
        )]
    )
    agents: List[Agent] = Field(
        default_factory=list,
        description="List of agent IDs that the user is subscribed to.",
        examples=[[
            Agent(
                agent_id="agent-123", name="Example Agent", icon_link=None, tags=["cool", "good"]
            )]]
    )
    models: List[LLMModel] = Field(
        default_factory=list,
        description="List of model IDs that the user has access to.",
        examples=[[
            LLMModel(
                model_id="model-123", name="Example Model", description="An example LLM model.", deployment_id="deployment-123", icon_link=None
            )
        ]]
    )


class GetConversationsResponse(BaseResponse):
    """
    GET /api/v1/conversations Response model
    """
    conversations: List[ConversationMaster] = Field(
        default_factory=list,
        description="List of conversations associated with the user.",
        examples=[[
            ConversationMaster(
                conversation_id=str(uuid.uuid4()),
                title="Cool Conversation",
                icon="😎",
                created_at="2023-10-01T12:00:00Z",
                updated_at="2023-10-01T12:00:00Z"
            )
        ]]
    )

class GetConversationResponse(BaseResponse):
    """
    GET /api/v1/conversation Response model
    """
    conversation: ConversationMaster = Field(
        ...,
        description="List of conversations associated with the user.",
        examples=[
            ConversationMaster(
                conversation_id=str(uuid.uuid4()),
                title="Cool Conversation",
                icon="😎",
                created_at="2023-10-01T12:00:00Z",
                updated_at="2023-10-01T12:00:00Z"
            )
        ]
    )
    messages: List[Message] = Field(
        default_factory=list,
        description="List of messages in the conversation.",
    )


class GetAvailableAgentsResponse(BaseResponse):
    """
    GET /api/v1/agents Response model
    """
    agents: List[Agent] = Field(
        default_factory=list,
        description="List of available agents.",
        examples=[[
            Agent(
                agent_id="agent-123", 
                name="Example Agent", 
                icon_link=None,
                tags=["cool", "good"]
            )
        ]]
    )
    total: int = Field(
        ...,
        description="Total number of agents matching the query.",
        examples=[103]
    )
    page: int = Field(
        description="Current page number.",
        ge=1,
        examples=[1]
    )
    size: int = Field(
        description="Number of items per page.",
        ge=1,
        examples=[20]
    )
    has_next: bool = Field(
        description="Whether there is a next page.",
        examples=[True]
    )

    


class GetAgentResponse(BaseResponse):
    """
    GET /api/v1/agent Response model
    """
    agent: AgentDetail = Field(
        ...,
        description="Details of the requested agent.",
        examples=[AgentDetail(
            agent_id="agent-123", 
            name="Example Agent", 
            icon_link=None,
            author_name="Author Name",
            description="This is an example agent.",
            tags=["cool", "good"],
            prompt="This is an example prompt for the agent.",
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now(),
        )]
    )


class PostSubscribeAgentResponse(BaseResponse):
    """
    POST /api/v1/agent/agent_id/subscribe Response model
    """
    pass


class PostPublishAgentResponse(BaseResponse):
    """
    POST /api/v1/agent/publish Response model
    """
    pass


class PutModifyAgentResponse(BaseResponse):
    """
    PUT /api/v1/agent/agent_id Response model
    """
    pass