import asyncio
import time
import os
import uuid
from typing import cast

from openai import AsyncOpenAI
from sqlalchemy.orm import Session
from pydantic import BaseModel

import backend._types as t
import backend.models as mdl
import backend.utils.logger as lg

from backend.utils.history import get_history, set_history
from backend.utils.agent_spec import get_agent_spec
from backend.utils.streamer import chunk

from agents.main import AsyncSimpleAgent


async def chat_completion(
    session: Session,
    request_id: str,
    user_profile: mdl.User,
    body: mdl.PostGenerateCompletionRequest
):
    start = time.time()
    yield await chunk(
        event="start", 
        data={"message": ""}, 
    )
    await asyncio.sleep(0.1)
    history, err = get_history(
        session=session,
        user_id=user_profile.user_id,
        conversation_id=body.conversation_id,
        request_id=request_id,
    )
    yield await chunk(
        event="status", 
        data={"message": "🧐 Analyzing your question..."}, 
    )
    await asyncio.sleep(0.1)
    if err:
        lg.logger.error(
            f"Error getting history for user {user_profile.user_id} in conversation {body.conversation_id}: {err}"
        )
        yield await chunk(
            "error", 
            {"message": "❌ Server sent error... Retry later."},
        )
        await asyncio.sleep(0.1)
        return
    lg.logger.info(
        f"History for user {user_profile.user_id} in conversation {body.conversation_id} retrieved successfully. Execution time: {time.time() - start:.2f} seconds."
    )
    
    user_message_id = str(uuid.uuid4())
    assaistant_message_id = str(uuid.uuid4())
    new_messages = []

    user = mdl.Message.user_message(
        message_id=user_message_id,
        parent_message_id=body.parent_message_id,
        agent_id=None,
        content=body.messages[0].content,
    )
    new_messages.append(user)
    await history.update_context(user)

    simple_agent = AsyncSimpleAgent(
        provider=AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    )
    
    lg.logger.info(
        f"Starting streaming user message ID {user_message_id}. Execution time: {time.time() - start:.2f} seconds. "
    )
    yield await chunk(
        event="status", 
        data={"message": "🤖 Generating Answers..."}, 
    )
    await asyncio.sleep(0.1)
    
    messages = [{"role": "system", "content": body.messages[0].content.parts[0]}]
    messages.extend(history.marshal_to_messagelike(user))
    
    gen = simple_agent.astream(
        messages=messages,
        deployment_id=body.llm.deployment_id
    )
    
    parts = ""
    async for response in gen:
        if response['type'] == 'delta':
            yield await chunk(
                event="data",
                data={"message": response['content']}
            )
            parts += response['content']
        elif response['type'] == 'done':
            yield await chunk(
                event="done",
                data={"message": response['content']}
            )
        elif response['type'] == 'error':
            yield await chunk(
                event="error",
                data={"message": response['content']}
            )
            return

        await asyncio.sleep(0.02)
    
    assistant = mdl.Message.assistant_message(
        message_id=assaistant_message_id,
        parent_message_id=user_message_id,
        agent_id=None,
        content=mdl.Content(type='text', parts=[parts]),
        llm_deployment_id=body.llm.deployment_id
    )
    new_messages.append(assistant)
    err = set_history(
        session=session,
        history=history,
        new_messages=new_messages,
        request_id=request_id,   
        conversation_type='chat'
    )
    if err:
        lg.logger.error(
            f"Error setting history for user {user_profile.user_id} in conversation {body.conversation_id}: {err}"
        )
        yield await chunk(
            "error", 
            {"message": "❌ Server sent error... Retry later."},
        )
        return