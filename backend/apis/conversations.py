import uuid
from typing import Annotated
from fastapi import APIRouter, Depends

import backend.constants as c
import backend.deps as dp
import backend.models.api as mdl

CONVERSATIONS = APIRouter(
    prefix=c.APIPrefix.CONVERSATIONS.value,
    tags=[c.APITag.CONVERSATIONS],
)

@CONVERSATIONS.get(
    path="",
    summary="Get User Conversations",
    description="Retrieves Conversations for the current user.",
    response_model=mdl.GetConversationsResponse,
)
def get_conversations(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
) -> mdl.GetConversationsResponse:
    
    return mdl.GetConversationsResponse(
        status="success",
        message="Conversations retrieved successfully.",
        request_id=request_id,
        conversations=[
            mdl.ConversationMaster(
                conversation_id=str(uuid.uuid4()),
                title="Cool Conversation Title",
                icon="😎",
                created_at="2023-10-01T12:00:00Z",
                updated_at="2023-10-01T12:00:00Z"
            )
        ]
    )


@CONVERSATIONS.get(
    path="/{conversation_id}",
    summary="Get Conversation Details",
    description="Retrieves details of a specific conversation by its ID.",
    response_model=mdl.GetConversationResponse,
)
def get_conversation(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    conversation_id: str,
) -> mdl.GetConversationResponse:
    
    return mdl.GetConversationResponse(
        status="success",
        message="Conversation details retrieved successfully.",
        request_id=request_id,
        conversation=mdl.ConversationMaster(
            conversation_id=conversation_id,
            title="Cool Conversation Title",
            icon="😎",
            created_at="2023-10-01T12:00:00Z",
            updated_at="2023-10-01T12:00:00Z"
        ),
        messages=[
            mdl.MessageResponse(
                message_id=str(uuid.uuid4()),
                content=mdl.Content(
                    type="text",
                    parts=["This is a message in the conversation."]
                ),
                role="user",
                parent_message_id=None,
                updated_at="2023-10-01T12:00:00Z",
                created_at="2023-10-01T12:00:00Z"
            )
        ]
    )