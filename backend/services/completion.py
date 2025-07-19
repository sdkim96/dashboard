import datetime as dt
import uuid

from sqlalchemy.orm import Session

import backend._types as t
import backend.models as mdl
import backend.utils.logger as lg

from backend.utils.history import get_history, set_history
from backend.utils.agent_spec import get_agent_spec

from agents.main import SimpleAgent

async def chunk(event: str, data: t.CompletionChunkUnion, delay: float | None) -> str:
    """
    Formats the event and data into a chunked string for streaming.

    Args:
        event (str): The event type.
        data (t.CompletionChunkUnion): The data to be sent. It can be a string, BaseModel, or dict.
        delay (float | None): Optional delay for the message.

    Returns:
        str: The formatted string for streaming.
    """
    delay = delay or 0.01
    completion = mdl.CompletionMessage(
        event=event,
        data=data,
        delay=delay
    )

    return await completion.to_stream()


async def chat_completion(
    session: Session,
    request_id: str,
    user_profile: mdl.User,
    body: mdl.PostGenerateCompletionRequest
):
    yield await chunk(
        event="start", 
        data={"message": "🤔 Think about your question..."}, 
        delay=0.01
    )
    history, err = get_history(
        session=session,
        user_id=user_profile.user_id,
        conversation_id=body.conversation_id,
        request_id=request_id,
    )
    if err:
        lg.logger.error(
            f"Error getting history for user {user_profile.user_id} in conversation {body.conversation_id}: {err}"
        )
        yield await chunk(
            "error", 
            {"message": "❌ Server sent error... Retry later."},
            0.01
        )
        return
    
    agent_spec, err = get_agent_spec(
        session=session,
        agent_id=body.agent_id,
        agent_version=body.agent_version,
        request_id=request_id,
    )
    if err:
        lg.logger.error(
            f"Error getting agent spec for agent {body.agent_id} version {body.agent_version}: {err}"
        )
        yield await chunk(
            "error", 
            {"message": "❌ Server sent error... Retry later."},
            0.01
        )
        return
    
    yield await chunk(
        event="data", 
        data={"message": "😎 Checked your selected agent's specification..."}, 
        delay=0.01
    )
    
    user_message_id = str(uuid.uuid4())
    assaistant_message_id = str(uuid.uuid4())
    messages = []

    user = mdl.Message.user_message(
        message_id=user_message_id,
        parent_message_id=body.parent_message_id,
        agent_id=None,
        content=body.messages[0].content,
        model=body.model
    )
    messages.append(user)
    
    yield await chunk(
        event="data", 
        data={"message": "🧐 Analyze what you said..."}, 
        delay=0.01
    )

    assistant = mdl.Message.assistant_message(
        message_id=assaistant_message_id,
        parent_message_id=user_message_id,
        agent_id=body.agent_id,
        content=mdl.Content(type='text', parts=["Generating response..."]),
        model=body.model
    )
    messages.append(assistant)
    
    err = set_history(
        session=session,
        history=history,
        new_messages=messages,
        request_id=request_id,   
    )
    if err:
        lg.logger.error(
            f"Error setting history for user {user_profile.user_id} in conversation {body.conversation_id}: {err}"
        )
        yield await chunk(
            "error", 
            {"message": "❌ Server sent error... Retry later."},
            0.01
        )
        return