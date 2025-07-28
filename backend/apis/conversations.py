import datetime as dt
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends

from sqlalchemy.orm import Session

import backend.constants as c
import backend.deps as dp
import backend.models as mdl
import backend.services.conversations as svc

CONVERSATIONS = APIRouter(
    prefix=c.APIPrefix.CONVERSATIONS.value,
    tags=[c.APITag.CONVERSATIONS],
)


@CONVERSATIONS.post(
    path="/new",
    summary="New Conversation",
    description="Creates a new conversation for the current user.",
    response_model=mdl.CreateConversationResponse,
)
async def new_conversation(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> mdl.CreateConversationResponse:
    
    return mdl.CreateConversationResponse(
        status="success",
        message="Conversation created successfully.",
        request_id=request_id,
        conversation_id=str(uuid.uuid4()),
        parent_message_id=None,
    )

@CONVERSATIONS.get(
    path="",
    summary="Get User Conversations",
    description="Retrieves Conversations for the current user.",
    response_model=mdl.GetConversationsResponse,
)
def get_conversations(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> mdl.GetConversationsResponse:

    conversations, err = svc.get_conversations(
        session=session,
        user_profile=user_profile,
        request_id=request_id,
    )
    if err:
        return mdl.GetConversationsResponse(
            status="error",
            message="Failed to retrieve conversations.",
            request_id=request_id,
            conversations=conversations
        )

    return mdl.GetConversationsResponse(
        status="success",
        message="Conversations retrieved successfully.",
        request_id=request_id,
        conversations=conversations
    )


@CONVERSATIONS.get(
    path="/{conversation_id}",
    summary="Get Conversation Details",
    description="Retrieves details of a specific conversation by its ID.",
    response_model=mdl.GetConversationResponse,
)
def get_conversation(
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    conversation_id: str,
) -> mdl.GetConversationResponse:
    
    conversation_type = 'chat'

    conversation, err = svc.get_conversation_by_id(
        session=session,
        user_profile=user_profile,
        request_id=request_id,
        conversation_id=conversation_id,
        conversation_type=conversation_type
    )
    if err:
        return mdl.GetConversationResponse(
            status="error",
            message="Failed to retrieve conversation details.",
            request_id=request_id,
            conversation=mdl.ConversationMaster.failed(),
            messages=[]
        )
    
    messages, err = svc.get_messages(
        session=session,
        user_profile=user_profile,
        request_id=request_id,
        conversation_id=conversation_id
    )
    if err:
        return mdl.GetConversationResponse(
            status="error",
            message="Failed to retrieve messages for the conversation.",
            request_id=request_id,
            conversation=conversation,
            messages=[]
        )
    
    return mdl.GetConversationResponse(
        status="success",
        message="Conversation details retrieved successfully.",
        request_id=request_id,
        conversation=conversation,
        messages=messages
    )