import datetime as dt
import json
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

import backend.models as mdl
import backend.db.user_tables as user_tbl
import backend.db.conversations_tables as tbl
import backend.utils.logger as lg

def get_conversations(
    session: Session,
    user_profile: mdl.User,
    request_id: str,
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
    