import uuid
import datetime as dt
from typing import List

from pydantic import BaseModel, Field

import backend._types as t
import backend.constants as c

from backend.models.user import User
from backend.models.agent import Agent, AgentDetail, AgentPublish, Attribute, AgentMarketPlace, AgentRequest
from backend.models.llm import LLMModel, LLMModelRequest
from backend.models.conversations import ConversationMaster
from backend.models.message import MessageRequest, MessageResponse, Content
from backend.models.tools import Tool, ToolMaster, ToolRequest
from backend.models.recommendations import RecommendationMaster, Recommendation

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
        examples=[AgentPublish.mock()]
    )


class PutModifyAgentRequest(BaseRequest):
    """
    POST /api/v1/agent/publish Request model
    """
    agent: AgentPublish = Field(
        ...,
        description="Details of the agent to be published.",
        examples=[AgentPublish.mock()]
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
    llm: LLMModelRequest = Field(
        ...,
        description="Model Deployment ID to be used for generating the completion.",
        examples=[LLMModelRequest(
            issuer="openai",
            deployment_id="deployment-123",
        )]
    )
    tools: List[ToolRequest] = Field(
        ...,
        description="List of tools to be used for generating the completion.",
        examples=[[ToolRequest.mock()]]
    )
    messages: List[MessageRequest] = Field(
        ...,
        description="List of messages in the conversation for which the completion is requested.",
        examples=[[MessageRequest(
            content=Content(type='text', parts=["Hello, how can I help you?"]),
        )]]
    )



class GetToolsRequest(BaseRequest):
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


class PostRescommendationRequest(BaseRequest):
    """
    POST /api/v1/recommendations Request model
    """
    work_details: str = Field(
        ...,
        description="Details of the recommendation to be created.",
        examples=[
            "This is a sample recommendation."
        ]
    )

class PostRecommendationCompletionRequest(BaseRequest):
    """
    POST /api/v1/recommendations/{recommendation_id}/completion Request model
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
    llm: LLMModelRequest = Field(
        ...,
        description="Model Deployment ID to be used for generating the completion.",
        examples=[LLMModelRequest(
            issuer="openai",
            deployment_id="deployment-123",
        )]
    )
    agent: AgentRequest = Field(
        ...,
        description="Agent to be used for generating the completion.",
        examples=[AgentRequest.mock()]
    )   
    messages: List[MessageRequest] = Field(
        ...,
        description="List of messages in the conversation for which the completion is requested.",
        examples=[[MessageRequest(
            content=Content(type='text', parts=["Hello, how can I help you?"]),
        )]]
    )

class GetConversationByRecommendationRequest(BaseRequest):
    """
    GET /api/v1/recommendations/{recommendation_id}/conversations Request model
    """
    agent_id: str = Field(
        ...,
        description="ID of the agent for which the conversation is requested.",
        examples=[str(uuid.uuid4())]
    )
    agent_version: int = Field(
        default=1,
        ge=0,
        description="Version of the agent for which the conversation is requested.",
        examples=[1]
    )

########################
## 2. Response Models ##
########################
class CreateConversationResponse(BaseResponse):
    """
    POST /api/v1/conversation/new Response model
    """
    conversation_id: str = Field(
        ...,
        description="ID of the newly created conversation.",
        examples=[str(uuid.uuid4())]
    )
    parent_message_id: None = Field(
        None,
        description="Parent message ID for the conversation, if applicable.",
        examples=[None]
    )
    
class GetMeResponse(BaseResponse):
    """
    GET /api/v1/user Response model
    """
    user: User = Field(
        ...,
        description="User information model containing details about the current user.",
        examples=[User.mock()]
    )
    llms: List[LLMModel] = Field(
        default_factory=list,
        description="List of model IDs that the user has access to.",
        examples=[[
            LLMModel.mock()
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
                created_at=dt.datetime.now(),
                updated_at=dt.datetime.now()
            )
        ]]
    )

class GetConversationResponse(BaseResponse):
    """
    GET /api/v1/conversation, /api/v1/recommendation/{recommendation_id}/conversations Response model
    """
    conversation: ConversationMaster = Field(
        ...,
        description="List of conversations associated with the user.",
        examples=[
            ConversationMaster(
                conversation_id=str(uuid.uuid4()),
                title="Cool Conversation",
                icon="😎",
                created_at=dt.datetime.now(),
                updated_at=dt.datetime.now()
            )
        ]
    )
    
    messages: List[MessageResponse] = Field(
        default_factory=list,
        description="List of messages in the conversation.",
    )


class GetAvailableAgentsResponse(BaseResponse):
    """
    GET /api/v1/agents Response model
    """
    agents: List[AgentMarketPlace] = Field(
        default_factory=list,
        description="List of available agents.",
        examples=[[
            AgentMarketPlace.mock()
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
    GET /api/v1/agents/{agent_id} Response model
    """
    agent: AgentDetail = Field(
        ...,
        description="Details of the requested agent.",
        examples=[AgentDetail.mock(type="BusinessSupport")],
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


class GetToolsResponse(BaseResponse):
    """
    GET /api/v1/tools Response model
    """
    tools: List[ToolMaster] = Field(
        default_factory=list,
        description="List of available tools.",
        examples=[[
            ToolMaster.mock()
        ]]
    )
    total: int = Field(
        ...,
        description="Total number of tools matching the query.",
        examples=[10]
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


class GetToolByIDResponse(BaseResponse):
    """
    GET /api/v1/tools/{tool_id} Response model
    """
    tool: Tool = Field(
        ...,
        description="Details of the requested tool.",
        examples=[Tool.mock()]
    )

class PostSubscribeToolResponse(BaseResponse):
    """
    POST /api/v1/tools/{tool_id}/subscribe Response model
    """
    pass


class GetRecommendationsResponse(BaseResponse):
    """
    GET /api/v1/recommendations Response model
    """
    total: int = Field(
        ...,
        description="Total number of tools matching the query.",
        examples=[10]
    )
    page: int = Field(
        description="Current page number.",
        ge=1,
        examples=[1]
    )
    size: int = Field(
        description="Number of items per page.",
        ge=0,
        examples=[20]
    )
    has_next: bool = Field(
        description="Whether there is a next page.",
        examples=[True]
    )
    recommendations: List[RecommendationMaster] = Field(
        default_factory=list,
        description="List of recommended tools for the user.",
        examples=[[
            RecommendationMaster.mock()
        ]]
    )

    @classmethod
    def mock(cls) -> "GetRecommendationsResponse":
        return cls(
            status="success",
            message="Recommendations retrieved successfully.",
            request_id=str(uuid.uuid4()),
            recommendations=[RecommendationMaster.mock()],
            total=1,
            page=1,
            size=20,
            has_next=False
        )
    

class GetRecommendationByIDResponse(BaseResponse):
    """
    GET /api/v1/recommendations/{recommendation_id} Response model
    """
    recommendation: Recommendation = Field(
        ...,
        description="Details of the requested recommendation.",
        examples=[Recommendation.mock()]
    )
    
    @classmethod
    def mock(cls) -> "GetRecommendationByIDResponse":
        return cls(
            status="success",
            message="Recommendation retrieved successfully.",
            request_id=str(uuid.uuid4()),
            recommendation=Recommendation.mock()
        )
    
class PostRecommendationResponse(BaseResponse):
    """
    POST /api/v1/recommendations Response model
    """
    recommendation: Recommendation = Field(
        ...,
        description="Details of the created recommendation.",
        examples=[Recommendation.mock()]
    )
    
    @classmethod
    def mock(cls) -> "PostRecommendationResponse":
        return cls(
            status="success",
            message="Recommendation created successfully.",
            request_id=str(uuid.uuid4()),
            recommendation=Recommendation.mock()
        )
    


class GetRecommendationConversationResponse(BaseResponse):
    """
    GET /api/v1/recommendations/{recommendation_id}/conversation Response model
    """
    conversation: ConversationMaster = Field(
        ...,
        description="List of conversations associated with the user.",
        examples=[
            ConversationMaster(
                conversation_id=str(uuid.uuid4()),
                title="Cool Conversation",
                icon="😎",
                created_at=dt.datetime.now(),
                updated_at=dt.datetime.now()
            )
        ]
    )
    
    messages: List[MessageResponse] = Field(
        default_factory=list,
        description="List of messages in the conversation.",
    )

    @classmethod
    def mock(cls) -> "GetRecommendationConversationResponse":
        return cls(
            status="success",
            message="Recommendation conversation retrieved successfully.",
            request_id=str(uuid.uuid4()),
            conversation=ConversationMaster.mock(),
            messages=[MessageResponse.mock()]
        )