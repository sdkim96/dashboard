import asyncio
import time
import uuid
from typing import cast

from sqlalchemy.orm import Session
from pydantic import BaseModel

import backend._types as t
import backend.models as mdl
import backend.utils.logger as lg

from backend.utils.history import get_history, set_history
from backend.utils.agent_spec import get_agent_spec

from agents.main import SimpleChat

async def chunk(event: str, data: t.CompletionChunkUnion) -> str:
    """
    Formats the event and data into a chunked string for streaming.

    Args:
        event (str): The event type.
        data (t.CompletionChunkUnion): The data to be sent. It can be a string, BaseModel, or dict.
        delay (float | None): Optional delay for the message.

    Returns:
        str: The formatted string for streaming.
    """
    completion = mdl.CompletionMessage(
        event=event,
        data=data,

    )
    buffer = await completion.to_stream()
    return buffer
    


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
    agent_spec, err = get_agent_spec(
        session=session,
        agent_id=body.agent_id,
        agent_version=body.agent_version,
        request_id=request_id,
    )
    
    lg.logger.info(
        f"Agent spec for agent {body.agent_id} version {body.agent_version} retrieved successfully. Execution time: {time.time() - start:.2f} seconds."
    )
    if err:
        lg.logger.error(
            f"Error getting agent spec for agent {body.agent_id} version {body.agent_version}: {err}"
        )
        yield await chunk(
            "error", 
            {"message": "❌ Server sent error... Retry later."},
        )
        return
    
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
    
    simple_agent = SimpleAgent(
        agent_id=body.agent_id,
        agent_version=body.agent_version,
        issuer=body.llm.issuer,
        deployment_id=body.llm.deployment_id,
    )
    
    lg.logger.info(
        f"Starting streaming for agent {body.agent_id} version {body.agent_version} with user message ID {user_message_id}. Execution time: {time.time() - start:.2f} seconds. "
    )
    yield await chunk(
        event="status", 
        data={"message": "🤖 Generating Answers..."}, 
    )
    await asyncio.sleep(0.1)
    
    parts = ""
    async for c in simple_agent.astream(
        messages=history.marshal_to_messagelike(
            user_message=user
        ),
        output_schema=[
            s.model_dump(mode="json") 
            for s in agent_spec.output_schema
        ] if agent_spec.output_schema else None,
    ):
        if agent_spec.output_schema:
            c = cast(BaseModel, c)
            part = c.model_dump_json()
            for p in part.split("\n"):
                print(p)
                if p.strip():
                    yield await chunk(
                        event="data", 
                        data={"message": f"{p}"},
                    )
                    await asyncio.sleep(0.02)
                    parts += p + "\n"
            
        else:
            async for part in c:
                match part.get("event"):
                    case "content.delta":
                        p = part.get("data", "")
                        parts += p
                        print(p)
                        yield await chunk(
                            event="data", 
                            data={"message": f"{p}"},
                        )
                        await asyncio.sleep(0.02)
                    case "content.done":
                        p = part.get("data", "")
                        yield await chunk(
                            event="done",
                            data={"message": f"{p}"},
                        )
                        await asyncio.sleep(0.02)
                

    # yield await chunk(
    #     event="done", 
    #     data={"message": parts},
    # )
    lg.logger.info(
        f"Streaming completed for agent {body.agent_id} version {body.agent_version} with user message ID {user_message_id}. Total execution time: {time.time() - start:.2f} seconds."
    )
    assistant = mdl.Message.assistant_message(
        message_id=assaistant_message_id,
        parent_message_id=user_message_id,
        agent_id=body.agent_id,
        content=mdl.Content(type='text', parts=[parts]),
        llm_deployment_id=body.llm.deployment_id
    )
    new_messages.append(assistant)
    
    err = set_history(
        session=session,
        history=history,
        new_messages=new_messages,
        request_id=request_id,   
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