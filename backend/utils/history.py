import datetime as dt
from typing import Optional, Tuple, List
from sqlalchemy import select, update, and_
from sqlalchemy.orm import Session

import backend.db.conversations_tables as tbl
import backend.db.tools_tables as tl_tbl
import backend.models as mdl
import backend._types as t

def get_history(
    session: Session,
    user_id: str,
    conversation_id: str,
    request_id: str,
    parent_message_id: str | None,
    limit: int = 10,
    *,
    conversation_type: t.ConversationTypeLiteral = 'chat'
) -> Tuple[mdl.History, Exception | None]:
    """
    Returns a history object.

    This function retrieves the conversation history for a given user and conversation ID.
    
    Returns:
        History: An empty history object.
    """
    Conversation = tbl.Conversation
    Message = tbl.Message
    ToolResult = tl_tbl.ToolResult

    stmt = (
        select(
            Conversation.conversation_id,
            Conversation.user_id,
            Conversation.title,
            Conversation.summary,
            Conversation.icon,
            Conversation.intent,
            Message.parent_message_id,
            Message.message_id,
            Message.content,
            Message.role,
            Message.llm_deployment_id,
            ToolResult.tool_id,
            ToolResult.output,
            Message.created_at,
            Message.updated_at
        )
        .join(
            Message, 
            Conversation.conversation_id == Message.conversation_id
        )
        .outerjoin(
        ToolResult,
        and_(
            ToolResult.conversation_id == Message.conversation_id,
            ToolResult.message_id == Message.message_id,
        ),
    )
        .where(Conversation.user_id == user_id)
        .where(Conversation.conversation_id == conversation_id)
        .where(Conversation.conversation_type == conversation_type)
        .order_by(Conversation.created_at.desc(), Message.created_at.desc())
    )
    try:
        results = session.execute(stmt).mappings().all()
        if len(results) == 0:
            return mdl.History(
                conversation_id=conversation_id,
                user_id=user_id,
                icon="😎",
                title="",
                summary="",
                messages=[],
                intent=""
            ), None

    except Exception as e:
        return mdl.History.failed(), ValueError(f"Error retrieving history: {e}")
    
    conversation = results[0]
    
    messages: List[mdl.Message] = []
    to_find = parent_message_id

    for msg in results:
        if to_find is None:
            continue
        if msg.message_id == to_find:
            parent = msg
            messages.append(
                mdl.Message(
                    message_id=parent.message_id,
                    parent_message_id=parent.parent_message_id,
                    tool_id=parent.tool_id,
                    tool_result=parent.tool_result,
                    role=parent.role,
                    content=mdl.Content.model_validate_json(parent.content),
                    created_at=parent.created_at,
                    updated_at=parent.updated_at,
                    llm_deployment_id=parent.llm_deployment_id
                )
            )
        to_find = parent.parent_message_id if parent else None

    history = mdl.History(
        conversation_id=conversation.conversation_id,
        user_id=conversation.user_id,
        title=conversation.title,
        icon=conversation.icon or "😎",
        summary=conversation.summary,
        messages=messages[:limit],
        intent=conversation.intent or "현재 의도가 존재하지 않습니다."
    )
    
    return history, None


def set_history(
    session: Session,
    history: mdl.History,
    new_messages: List[mdl.Message],
    request_id: str ,
    *,
    conversation_type: t.ConversationTypeLiteral = 'chat'
) -> ValueError | None:
    """
    Sets the history object.

    This function adds a new message to the conversation history in the database.
    
    Args:
        history (History): The history object to set.

    Returns:
        ValueError | None: Returns None if successful, otherwise returns a ValueError.
    """
    if len(new_messages) == 0:
        return ValueError("No new messages to set in history.")

    if history.is_empty:
        session.add(
            tbl.Conversation(
                conversation_id=history.conversation_id,
                user_id=history.user_id,
                title=history.title,
                intent=history.intent,
                summary=history.summary,
                icon=history.icon or "😎",
                conversation_type=conversation_type,
                created_at=dt.datetime.now(),
                updated_at=dt.datetime.now()
            )
        )
    else:
        updated_at = dt.datetime.now()
        updt= update(
            tbl.Conversation
        ).where(
            tbl.Conversation.conversation_id == history.conversation_id
        ).values(
            title=history.title,
            summary=history.summary,
            icon=history.icon or "😎",
            intent=history.intent,
            updated_at=updated_at
        )
        session.execute(updt)
    
    for new_message in new_messages:
        orm = tbl.Message(
            message_id=new_message.message_id,
            conversation_id=history.conversation_id,
            parent_message_id=new_message.parent_message_id,
            role=new_message.role,
            content=new_message.content.model_dump_json(),
            llm_deployment_id=new_message.llm_deployment_id,
            created_at=new_message.created_at,
            updated_at=new_message.updated_at,
        )
        tool_orm = tl_tbl.ToolResult(
            conversation_id=history.conversation_id,
            message_id=new_message.message_id,
            tool_id=new_message.tool_id,
            output=new_message.tool_result,
            created_at=new_message.created_at,
            updated_at=new_message.updated_at,  
        ) if new_message.tool_id else None
        session.add(orm)
        if tool_orm:
            session.add(tool_orm)

    try:
        session.commit()
        return None
    except Exception as e:
        session.rollback()
        return ValueError(f"Error setting history: {e}")