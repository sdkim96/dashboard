from typing import List, Optional, Tuple

from sqlalchemy import select, and_
from sqlalchemy.orm import Session

import backend.models as mdl
import backend.db.tools_tables as tl_tbl
import backend.db.conversations_tables as tbl
import backend.utils.logger as lg
import backend._types as t

def get_conversations(
    session: Session,
    user_profile: mdl.User,
    request_id: str,
    *,
    conversation_type: t.ConversationTypeLiteral = 'chat'
) -> Tuple[List[mdl.ConversationMaster], Exception | None]:
    
    Conversation = tbl.Conversation
    result = []

    stmt = (
        select(
            Conversation.conversation_id,
            Conversation.title,
            Conversation.icon,
            Conversation.created_at,
            Conversation.updated_at
        )
        .where(
            Conversation.user_id == user_profile.user_id
        )
        .where(
            Conversation.conversation_type == conversation_type
        )
        .order_by(Conversation.updated_at.desc())
    )
    try:
        conversations = session.execute(stmt).mappings().all()
    except Exception as e:
        lg.logger.error(f"Error retrieving conversations for user {user_profile.user_id}: {e}")
        return result, e
        
    for cvs in conversations:
        result.append(
            mdl.ConversationMaster(
                conversation_id=cvs.conversation_id,
                title=cvs.title,
                icon=cvs.icon or "😎",
                created_at=cvs.created_at,
                updated_at=cvs.updated_at
            )
        )

    return result, None
    
def get_conversation_by_id(
    session: Session,
    user_profile: mdl.User,
    request_id: str,
    conversation_id: str,
    conversation_type: t.ConversationTypeLiteral = 'chat'
) -> Tuple[mdl.ConversationMaster, Exception | None]:
    Conversation = tbl.Conversation

    stmt = (
        select(
            Conversation.conversation_id,
            Conversation.title,
            Conversation.icon,
            Conversation.created_at,
            Conversation.updated_at
        )
        .where(
            Conversation.user_id == user_profile.user_id,
            Conversation.conversation_id == conversation_id,
            Conversation.conversation_type == conversation_type
        )
    )

    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    
    try:
        conversation = session.execute(stmt).mappings().one_or_none()
    except Exception as e:
        lg.logger.error(f"Error retrieving conversation {conversation_id} for user {user_profile.user_id}: {e}")
        return mdl.ConversationMaster.failed(), e

    if not conversation:
        return mdl.ConversationMaster.failed(), None

    return mdl.ConversationMaster(
        conversation_id=conversation.conversation_id,
        title=conversation.title,
        icon=conversation.icon or "😎",
        created_at=conversation.created_at,
        updated_at=conversation.updated_at
    ), None

def get_messages(
    session: Session,
    user_profile: mdl.User,
    request_id: str,
    conversation_id: str
) -> Tuple[List[mdl.MessageResponse], Exception | None]:
    
    Conversation = tbl.Conversation
    Message = tbl.Message
    LLM = tbl.LLMIssuer
    ToolResult = tl_tbl.ToolResult

    stmt = (
        select(
            Message.message_id,
            Message.content,
            Message.role,
            Message.llm_deployment_id,
            Message.parent_message_id,
            ToolResult.tool_id,
            ToolResult.output.label("tool_result"),
            Message.created_at.label("message_created_at"),
            Message.updated_at.label("message_updated_at"),
            LLM.issuer,
            LLM.name,
            LLM.description,
            LLM.icon_link
        )
        .join(
            Conversation,
            Conversation.conversation_id == Message.conversation_id
        )
        .join(
            LLM,
            LLM.deployment_id == Message.llm_deployment_id,
            isouter=True
        )
        .join(
            ToolResult,
            and_(
                ToolResult.conversation_id == Message.conversation_id,
                ToolResult.message_id == Message.message_id,
            ),
            isouter=True
        )
        .where(
            Conversation.user_id == user_profile.user_id,
            Conversation.conversation_id == conversation_id
        )
        .order_by(Message.created_at.asc())
    )

    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    
    try:
        messages = session.execute(stmt).mappings().all()
    except Exception as e:
        lg.logger.error(f"Error retrieving conversation {conversation_id} for user {user_profile.user_id}: {e}")
        return [], e

    result = []
    for msg in messages:
        content = mdl.Content.model_validate_json(msg.content)
        
        if msg.role == 'user':
            llm = None
        else:
            llm = mdl.LLMModel(
                issuer=msg.issuer,
                deployment_id=msg.llm_deployment_id,
                name=msg.name,
                description=msg.description,
                icon_link=msg.icon_link
            )

        result.append(
            mdl.MessageResponse(
                message_id=msg.message_id,
                content=mdl.Content(
                    type=content.type,
                    parts=content.parts
                ),
                role=msg.role,
                llm=llm,
                tool_id=msg.tool_id,
                tool_result=msg.tool_result,
                parent_message_id=msg.parent_message_id,
                updated_at=msg.message_updated_at,
                created_at=msg.message_created_at
            )
        )
       
    return result, None