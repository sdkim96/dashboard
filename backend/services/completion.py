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
    lg.logger.info(
f"""
---
💬 API: Chat Completion
유저: {user_profile.username}
질문: {body.messages[0].content.parts[0]}
사용예정 LLM: {body.llm.deployment_id}
사용예정 도구ID: {body.tools}
시작시간: {start:.2f}
---
"""
    )
    yield await chunk(
        event="start", 
        data={"message": ""}, 
    )
    await asyncio.sleep(0.02)
    history, err = get_history(
        session=session,
        user_id=user_profile.user_id,
        conversation_id=body.conversation_id,
        request_id=request_id,
        parent_message_id=body.parent_message_id
    )
    if err:
        lg.logger.error(
f"""
Raises
---
위치: get_history
유저: {user_profile.username}
오류 메시지: {err}
---
"""
        )
        yield await chunk(
            "error", 
            {"message": "❌ 서버 내부 오류가 발생하였습니다. 나중에 다시 시도해주세요."},
        )
        await asyncio.sleep(0.1)
        return
    tools, err = get_tools_by_ids(session=session, tool_ids=[t.tool_id for t in body.tools])
    if err:
        lg.logger.error(
f"""
Raises
---
위치: get_tools_by_ids
유저: {user_profile.username}
오류 메시지: {err}
---
"""
        )
        yield await chunk(
            "error", 
            {"message": "❌ 서버 내부 오류가 발생하였습니다. 나중에 다시 시도해주세요."},
        )
        await asyncio.sleep(0.1)
        return
    
    
    yield await chunk(
        event="status", 
        data={"message": "🧐 사용자님의 질문을 분석중입니다..."}, 
    )
    await asyncio.sleep(0.1)
    lg.logger.info(
f"""
---
🛠️ 히스토리와 사용할 도구의 스펙을 가져왔습니다.
유저: {user_profile.username}
걸린 시간: {time.time() - start:.2f}초
---
"""
    )
    if len(tools) == 0:
        yield await chunk(
            event="status", 
            data={"message": (
f"""
💭 사용자님은 따로 도구사용을 안하셨어...
☺️ 이 문제를 해결하기 위해서 사용자님의 질문을 분석해보겠습니다!
"""
            )}, 
        )
    else:  
        yield await chunk(
            event="status", 
            data={"message": (
f"""
💭 사용자님은 다음과 같은 도구들로 문제를 해결하기를 원하시고 계셔...

{", ".join([f"🛠️ {t.tool_name}" for t in tools]) if tools else "사용할 도구가 없습니다."}

☺️ 이 문제를 해결하기 위해서 사용자님의 질문을 분석해보겠습니다!
"""
            )}, 
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
    lg.logger.info(
f"""
---
📊 현재 히스토리의 맥락(컨텍스트)를 업데이트 완료하였습니다.
유저: {user_profile.username}
걸린 시간: {time.time() - start:.2f}초
---
"""
    )
    yield await chunk(
        event="status", 
        data={"message": (
f"""
💭 사용자님은 **{history.intent}**를 하고자 하셔... 이 문제를 해결하기 위해서 어떤 해결책이 있을까? 🤔
"""
        )}, 
    )
    await asyncio.sleep(0.02)
    selected_tools = [
        ToolSpec.model_validate(tool) 
        for tool in await choose_tools(tools)
    ]
    simple_agent = AsyncSimpleAgent(
        provider=AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        ),
        tools=selected_tools,
        user_context=history.get_context() or "사용자 맥락이 존재하지 않습니다."
    )
    
    messages = [{"role": "system", "content": body.messages[0].content.parts[0]}]
    messages.extend(history.marshal_to_messagelike(user))
    lg.logger.info(
f"""
---
🤖 현재 정보를 바탕으로 스트리밍 예정입니다...
유저: {user_profile.username}
걸린 시간: {time.time() - start:.2f}초
---
"""
    )
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
            lg.logger.error(
f"""
Raises
---
위치: get_tools_by_ids
유저: {user_profile.username}
오류 메시지: {err}
---
"""
            )
            yield await chunk(
                event="error",
                data={"message": response['content']}
            )
            return

        await asyncio.sleep(0.02)

    final_tool_id = None
    final_tool_result = None
    for resp in tool_results:
        for t in tools:
            if resp.name == t.tool_name:
                lg.logger.info(
f"""
---
🛠️ 해당 도구: {t.tool_name}에 대해 작업결과는 다음과같습니다.
유저: {user_profile.username}
걸린 시간: {time.time() - start:.2f}초
도구 결과 앞부분: {resp.output[:100]}...
---
"""
    )
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
    
    lg.logger.info(
f"""
---
💬 API: Chat Completion 완료
유저: {user_profile.username}
걸린 시간: {time.time() - start:.2f}초
---
"""
    )