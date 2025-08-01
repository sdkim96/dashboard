import datetime as dt
from typing import Optional, Tuple, List
from sqlalchemy import select, update
from sqlalchemy.orm import Session

import backend.db.conversations_tables as tbl
import backend.models as mdl
import backend._types as t

def get_history(
    session: Session,
    user_id: str,
    conversation_id: str,
    request_id: str,
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

    stmt = (
        select(
            Conversation.conversation_id,
            Conversation.user_id,
            Conversation.title,
            Conversation.summary,
            Conversation.icon,
            Message.agent_id,
            Message.parent_message_id,
            Message.message_id,
            Message.content,
            Message.role,
            Message.llm_deployment_id,
            Message.created_at,
            Message.updated_at
        )
        .join(
            Message, 
            Conversation.conversation_id == Message.conversation_id
        )
        .where(Conversation.user_id == user_id)
        .where(Conversation.conversation_id == conversation_id)
        .where(Conversation.conversation_type == conversation_type)
        .order_by(Conversation.created_at.desc(), Message.created_at.desc())
        .limit(limit)
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
                messages=[]
            ), None

    except Exception as e:
        return mdl.History.failed(), ValueError(f"Error retrieving history: {e}")
    
    conversation = results[0]
    messages = [
        mdl.Message(
            message_id=msg.message_id,
            parent_message_id=msg.parent_message_id,
            agent_id=msg.agent_id,
            role=msg.role,
            content=mdl.Content.model_validate_json(msg.content),
            created_at=msg.created_at,
            updated_at=msg.updated_at,
            llm_deployment_id=msg.llm_deployment_id
        ) for msg in results
    ]

    history = mdl.History(
        conversation_id=conversation.conversation_id,
        user_id=conversation.user_id,
        title=conversation.title,
        icon=conversation.icon or "😎",
        summary=conversation.summary,
        messages=messages
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
            updated_at=updated_at
        )
        session.execute(updt)
    
    for new_message in new_messages:
        orm = tbl.Message(
            message_id=new_message.message_id,
            conversation_id=history.conversation_id,
            parent_message_id=new_message.parent_message_id,
            agent_id=new_message.agent_id,
            role=new_message.role,
            content=new_message.content.model_dump_json(),
            llm_deployment_id=new_message.llm_deployment_id,
            created_at=new_message.created_at,
            updated_at=new_message.updated_at,
        )
        session.add(orm)

    try:
        session.commit()
        return None
    except Exception as e:
        session.rollback()
        return ValueError(f"Error setting history: {e}")