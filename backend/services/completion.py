import asyncio
import time
import os
import uuid
from typing import List

from openai import AsyncOpenAI
from sqlalchemy.orm import Session

import backend.models as mdl

import backend.utils.logger as lg
from backend.utils.history import get_history, set_history
from backend.utils.streamer import chunk
from backend.utils.tool_pools import choose_tools

from backend.services.tools import get_tools_by_ids

from agents.main import AsyncSimpleAgent
from agents.tools import ToolSpec, ToolResponse


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
        parent_message_id=body.parent_message_id
    )
    tools, err = get_tools_by_ids(session=session, tool_ids=[t.tool_id for t in body.tools])
    
    if err:
        lg.logger.error(
            f"Error getting tool spec for user {user_profile.user_id} in conversation {body.conversation_id}: {err}"
        )
        yield await chunk(
            "error", 
            {"message": "❌ Server sent error... Retry later."},
        )
        await asyncio.sleep(0.1)
        return
    
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
    await history.update_context(
        current_user_message=user, 
        parent_message_id=body.parent_message_id
    )
    yield await chunk(
        event="status", 
        data={"message": "🤔 Studying your question pattern..."}, 
    )
    await asyncio.sleep(0.1)
    tools_chosen = await choose_tools(tools)

    selected_tools = [ToolSpec.model_validate(tool) for tool in tools_chosen]

    if len(selected_tools) == 0:
        selected_tools = []

    simple_agent = AsyncSimpleAgent(
        provider=AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        tools=selected_tools,
        user_context=history.get_context() or "사용자 맥락이 존재하지 않습니다."
    )
    
    lg.logger.info(
        f"Starting streaming user message ID {user_message_id}. Execution time: {time.time() - start:.2f} seconds. "
    )
    
    messages = [{"role": "system", "content": body.messages[0].content.parts[0]}]
    messages.extend(history.marshal_to_messagelike(user))
    yield await chunk(
        event="status", 
        data={"message": "😎 Check your context..."}, 
    )
    await asyncio.sleep(0.1)
    gen = simple_agent.astream_v2(
        messages=messages,
        deployment_id=body.llm.deployment_id
    )
    
    parts = ""
    tool_results: List[ToolResponse] = []
    async for response in gen:
        if response['type'] == 'tool':
            tool_results.append(ToolResponse.model_validate_json(response['content']))
        elif response['type'] == 'delta':
            yield await chunk(
                event="data",
                data={"message": response['content']}
            )
            await asyncio.sleep(0.02)
            lg.logger.debug(f"Streaming: {response['content']}")
            parts += response['content']
        elif response['type'] == 'done':
            yield await chunk(
                event="done",
                data={"message": response['content']}
            )
            await asyncio.sleep(0.1)
        elif response['type'] == 'status':
            yield await chunk(
                event="status",
                data={"message": response['content']}
            )
            await asyncio.sleep(0.1)
        elif response['type'] == 'error':
            lg.logger.error(f"Error in streaming: {response['content']}")
            yield await chunk(
                event="error",
                data={"message": response['content']}
            )
            return

        await asyncio.sleep(0.02)

    final_tool_id = None
    final_tool_result = None
    for resp in tool_results:
        lg.logger.info(f"Tool executed: {resp.name}, success: {resp.success}, output: {resp.output}")
        for t in tools:
            if resp.name == t.tool_name:
                final_tool_id = t.tool_id
                final_tool_result = resp.output
                break
            
    assistant = mdl.Message.assistant_message(
        message_id=assaistant_message_id,
        parent_message_id=user_message_id,
        content=mdl.Content(type='text', parts=[parts]),
        llm_deployment_id=body.llm.deployment_id,
        tool_id=final_tool_id,
        tool_result=final_tool_result
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