import asyncio
import os
import httpx
import time
import datetime as dt
import collections
import uuid
from typing import Tuple, List

from openai import AsyncOpenAI
from sqlalchemy import select, func, distinct, update
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

import backend.db.agent_tables as tbl
import backend.db.recommendation_tables as rec_tbl
import backend.models as mdl

from agents.main import AsyncSimpleAgent
from agents.registry import AgentRegistry

import backend.config as cfg
import backend.utils.logger as lg
from backend.utils.history import get_history, set_history
from backend.utils.specs import get_agent_spec
from backend.utils.streamer import chunk

class AnalyzedContext(BaseModel):
    title: str = Field(
        ...,
        description="분석된 맥락의 제목입니다.",
        examples=["유저의 휴가 기안문 작성"]
    )
    context: str = Field(
        ...,
        description="분석되는 특정 맥락입니다.",
        examples=["유저는 현재 휴가를 신청하려고 합니다. 휴가는 2023년 12월 1일부터 2023년 12월 10일까지입니다. 유저는 휴가 기안문을 작성해야 합니다."]
    )
    problems: List[str] = Field(
        ...,
        description="유저가 직면한 문제를 나열합니다.",
        examples=[
            "팀원 간의 의사소통 부족.",
            "다가오는 분기의 불명확한 판매 목표.",
            "프로젝트 마감일이 임박했지만 리소스가 부족함.",
            "휴가에 대한 깊은 열망"
        ]
    )
    loacation: str = Field(
        ...,
        description="유저의 문제나 맥락, 메시지에서 언급된 장소입니다. 혹은 회의록등에서 언급된 장소입니다.",
        examples=["서울, 대한민국", "부서 회의실", "온라인 회의"]
    )
    participants: List[str] = Field(
        ...,
        description="맥락에 관련된 참여자 목록입니다.",
        examples=["John Doe", "Jane Smith"]
    )

    def description(self) -> str:
        """
        Returns a description of the context.
        """
        return f"""
## {self.title}
시기: {dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
장소: {self.loacation}
참여자: {', '.join(self.participants)}

### 맥락
{self.context}

### 문제
- {', '.join(self.problems)}
        
        """

def _get_agent_details(
    session: Session,
) -> Tuple[List[mdl.Agent], Exception | None]:
    
    Master = tbl.Agent
    Detail = tbl.AgentDetail
    Tags = tbl.AgentTag

    results: List[mdl.Agent] = []
    stmt = (
        select(
            Master.agent_id,
            Detail.version,
            Master.department_name,
            Detail.description,
            Master.name,
            func.array_agg(Tags.tag).label("tags"),
            Detail.icon_link,
            Detail.created_at,
            Detail.updated_at,
        )
        .join(
            Detail,
            Master.agent_id == Detail.agent_id
        )
        .outerjoin(
            Tags,
            Master.agent_id == Tags.agent_id
        )
        .where(
            Detail.is_active.is_(True),
            Detail.is_deleted.is_(False),
        )
        .group_by(
            Master.agent_id,
            Detail.version,
            Master.department_name,
            Detail.description,
            Master.name,
            Detail.icon_link,
            Detail.created_at,
            Detail.updated_at,
        )
    )
    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    try:
        agents = session.execute(stmt).mappings().all()
    except Exception as e:
        return [], e
    
    for agent in agents:
        results.append(
            mdl.Agent(
                agent_id=agent.agent_id,
                agent_version=agent.version,
                department_name=agent.department_name,
                description=agent.description,
                name=agent.name,
                tags=agent.tags or [],
                icon_link=agent.icon_link,
                created_at=agent.created_at,
                updated_at=agent.updated_at,
            )
        )
    
    return results, None


def _add_recommendation(
    session: Session,
    recommendation: mdl.Recommendation,
    title: str,
    description: str,
    user_id: str,
) -> Tuple[bool, Exception | None]:
    """
    Add a recommendation to the database.

    Args:
        session (Session): Database session dependency.
        recommendation (mdl.Recommendation): The recommendation to add.

    Returns:
        Tuple[mdl.Recommendation, Exception | None]: The added recommendation and any error encountered.
    """
    Recommendation = rec_tbl.Recommendation
    RecommendationAgents = rec_tbl.RecommendationAgents

    session.add(
        Recommendation(
            recommendation_id=recommendation.recommendation_id,
            title=title,
            description=description,
            user_id=user_id,
            work_when=recommendation.work_when,
            work_where=recommendation.work_where,
            work_whom=recommendation.work_whom,
            work_details=recommendation.work_details,
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now(),
        )
    )
    for dept_agents in recommendation.agents:
        for rec_agent in dept_agents.agents:
            recommended = RecommendationAgents(
                recommendation_id=recommendation.recommendation_id,
                agent_id=rec_agent.agent_id,
                agent_version=rec_agent.agent_version,
                created_at=dt.datetime.now(),
                updated_at=dt.datetime.now(),
            )
            session.add(recommended)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        return False, e

    return True, None


def _add_recommendation_conversation(
    session: Session,
    recommendation_id: str,
    agent_id: str,
    agent_version: int,
    conversation_id: str,
    user_message_id: str,
    assistant_message_id: str
) -> Exception | None:
    """
    Add a conversation to the recommendation.

    Args:
        session (Session): Database session dependency.
        recommendation_id (str): The ID of the recommendation.
        conversation_id (str): The ID of the conversation.

    Returns:
        Exception | None: An error if the conversation could not be added, otherwise None.
    """
    RecommendationConversations = rec_tbl.RecommendationConversations

    for id in [user_message_id, assistant_message_id]:
        session.add(
            RecommendationConversations(
                recommendation_id=recommendation_id,
                agent_id=agent_id,
                agent_version=agent_version,
                conversation_id=conversation_id,
                message_id=id,
            )
        )

    try:    
        session.commit()
    except Exception as e:
        session.rollback()
        return e

    return None


def get_recommendation_masters(
    session: Session,
    user_profile: mdl.User
) -> Tuple[List[mdl.RecommendationMaster], Exception | None]:
    results = []
    
    Recommendation = rec_tbl.Recommendation
    RecommendationAgents = rec_tbl.RecommendationAgents
    Agent = tbl.Agent

    stmt = (
        select(
            Recommendation.recommendation_id,
            Recommendation.title,
            Recommendation.description,
            Recommendation.created_at,
            Recommendation.updated_at,
            func.array_agg(distinct(Agent.department_name)).label("departments"),
        )
        .join(
            RecommendationAgents,
            Recommendation.recommendation_id == RecommendationAgents.recommendation_id
        )
        .join(
            Agent,
            RecommendationAgents.agent_id == Agent.agent_id
        )
        .where(
            Recommendation.user_id == user_profile.user_id,
            Recommendation.is_deleted.is_(False)
        )
        .group_by(
            Recommendation.recommendation_id,
            Recommendation.title,
            Recommendation.description,
            Recommendation.created_at,
            Recommendation.work_where,
        )
        .order_by(Recommendation.created_at.desc())
    )
    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    try:
        recommendations = session.execute(stmt).mappings().all()
    except Exception as e:
        return [], e
    
    for rec in recommendations:
        results.append(
            mdl.RecommendationMaster(
                recommendation_id=rec.recommendation_id,
                title=rec.title,
                description=rec.description,
                created_at=rec.created_at,
                updated_at=rec.updated_at,
                departments=rec.departments or [],
            )
        )
    return results, None

def get_recommendation_by_id(
    session: Session,
    user_profile: mdl.User,
    recommendation_id: str
) -> Tuple[mdl.Recommendation, Exception | None]:
    """
    Get a recommendation by its ID.

    Args:
        session (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.
        recommendation_id (str): The ID of the recommendation to retrieve.

    Returns:
        mdl.Recommendation: The requested recommendation.
    """

    Recommendation = rec_tbl.Recommendation
    RecommendedAgents = rec_tbl.RecommendationAgents
    Agent = tbl.Agent
    AgentDetail = tbl.AgentDetail
    AgentTag = tbl.AgentTag

    stmt = (
        select(
            Recommendation.recommendation_id,
            Recommendation.work_when,
            Recommendation.work_where,
            Recommendation.work_whom,
            Recommendation.work_details,
            RecommendedAgents.agent_id,
            RecommendedAgents.agent_version,
            Agent.department_name,
            Agent.name,
            AgentDetail.description,
            func.array_agg(AgentTag.tag).label("tags"),
            AgentDetail.icon_link,
            AgentDetail.created_at,
            AgentDetail.updated_at,
        )
        .join(
            RecommendedAgents,
            Recommendation.recommendation_id == RecommendedAgents.recommendation_id
        )
        .join(
            AgentDetail,
            (RecommendedAgents.agent_id == AgentDetail.agent_id) &
            (RecommendedAgents.agent_version == AgentDetail.version) 
        )
        .join(
            Agent,
            RecommendedAgents.agent_id == Agent.agent_id
        )
        .outerjoin(
            AgentTag,
            Agent.agent_id == AgentTag.agent_id
        )
        .where(Recommendation.recommendation_id == recommendation_id)
        .where(Recommendation.user_id == user_profile.user_id)
        .group_by(
            Recommendation.recommendation_id,
            Recommendation.work_when,
            Recommendation.work_where,
            Recommendation.work_whom,
            Recommendation.work_details,
            RecommendedAgents.agent_id,
            RecommendedAgents.agent_version,
            Agent.department_name,
            Agent.name,
            AgentDetail.description,
            AgentDetail.icon_link,
            AgentDetail.created_at,
            AgentDetail.updated_at,
        )
    )
    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    try:
        recommendations = session.execute(stmt).mappings().all()
    except Exception as err:
        lg.logger.error(f"Error retrieving recommendation: {err}")
        return mdl.Recommendation.failed(), err
    
    if len(recommendations) == 0:
        return mdl.Recommendation.failed(), None
    
    rec_agents = []
    for agent in recommendations:
        rec_agents.append(
            mdl.AgentRecommendation(
                department_name=agent.department_name,
                agents=[
                    mdl.Agent(
                        agent_id=agent.agent_id,
                        agent_version=agent.agent_version,
                        name=agent.name,
                        department_name=agent.department_name,
                        description=agent.description,
                        tags=agent.tags or [],
                        icon_link=agent.icon_link,
                        created_at=agent.created_at,
                        updated_at=agent.updated_at,
                    )
                ]
            )
        )

    
    rcmd = mdl.Recommendation(
        recommendation_id=recommendations[0].recommendation_id,
        work_when=recommendations[0].work_when,
        work_where=recommendations[0].work_where,
        work_whom=recommendations[0].work_whom,
        work_details=recommendations[0].work_details,
        agents=rec_agents
    )
    
    return rcmd, None

async def create_recommendation(
    session: Session,
    user_profile: mdl.User,
    body: mdl.PostRescommendationRequest,
    request_id: str
) -> Tuple[mdl.Recommendation, Exception | None]:
    """
    Create a new recommendation for the user.

    Args:
        session (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.
        body (mdl.PostRescommendationRequest): The request body containing recommendation details.

    Returns:
        Tuple[mdl.Recommendation, Exception | None]: The created recommendation and any error encountered.
    """
    lg.logger.info(
        f"Creating recommendation for user {user_profile.user_id} with request ID {request_id}"
    )
    recommendation_id= "rec-" + str(uuid.uuid4())
    work_when = dt.datetime.now()

    simple_agent = AsyncSimpleAgent(
        provider=AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    )
    system_prompt=(
            """ 
## Role
당신은 유저의 문제를 이해하는 AI 어시스턴트입니다.
유저는 반드시 **특정 기업부서에서 일하는 사람입니다.** 이와 관련된 문제를 회사와 해결함에 있습니다.

## Task
- 유저의 질문을 읽고 그가 처한 문제를 이해합니다.
- 유저의 질문에 기반하여 그가 처한 맥락을 제공합니다.
- 맥락은 **한국어**로 반환해야 합니다.
- 그의 문제와 맥락을 명확하게 리스트업하세요.
            """
    )


    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": body.work_details}
    ]

    context, err= await simple_agent.aparse(
        messages=messages,
        deployment_id="gpt-5-nano",
        response_fmt=AnalyzedContext
    )
    lg.logger.info(
        f"Context analyzed for user {user_profile.user_id}: {context}"
    )
    if err or not context:
        return mdl.Recommendation.failed(), err
    
    
    agent_details, err = _get_agent_details(session=session)
    if err:
        return mdl.Recommendation.failed(), err
    registry = AgentRegistry(
        agent_cards=[agent.model_dump(mode="json") for agent in agent_details],
    )
    search_results, err = await registry.asearch_by_ai(
        "최적의 AI 에이전트들을 찾아줘 이유와 점수를 함께 알려줘",
        context=context.description(),
        search_engine=simple_agent
    )
    lg.logger.info(
        f"Search results for user {user_profile.user_id}: {search_results}"
    )
    if err:
        return mdl.Recommendation.failed(), err

    
    recommended_depts = collections.defaultdict(list)
    for result in search_results:
        recommended_depts[result["department_name"]].append(mdl.Agent.model_validate(result))

    results = []
    for k, v in recommended_depts.items():
        results.append(
            mdl.AgentRecommendation(
                department_name=k,
                agents=v
            )
        )

    _add_recommendation(
        session=session,
        recommendation=mdl.Recommendation(
            recommendation_id=recommendation_id,
            work_when=work_when,
            work_where=context.loacation,
            work_whom=", ".join(context.participants),
            work_details=body.work_details,
            agents=results
        ),
        title=context.title,
        description=context.context,
        user_id=user_profile.user_id
    )
    
    return mdl.Recommendation(
        recommendation_id=recommendation_id,
        work_when = work_when,
        work_where= context.loacation,
        work_whom="".join(context.participants),
        work_details=body.work_details,
        agents=results
    ), None


async def chat_completion_with_agent(
    session: Session,
    user_profile: mdl.User,
    recommendation_id: str,
    body: mdl.PostRecommendationCompletionRequest,
    request_id: str
):
    """
    Create a new recommendation by interacting with an agent.
    This function handles the interaction with an agent to create a recommendation.

    Args:
        session (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.
        body (mdl.PostRecommendationCompletionRequest): The request body containing interaction details.
        request_id (str): The unique request ID for tracking.
    Returns:
        StreamingResponse: A streaming response containing the generated recommendation.
    """
    start = time.time()
    lg.logger.info(
f"""
---
💬 API: Chat Completion With Agent
유저: {user_profile.username}
질문: {body.messages[0].content.parts[0]}
사용예정 LLM: {body.llm.deployment_id}
사용에이전트: {body.agent.agent_id} v{body.agent.agent_version}
시작시간: {start:.2f}
---
"""
    )
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
        conversation_type='recommendation',
        parent_message_id=body.parent_message_id
    )
    yield await chunk(
        event="status", 
        data={"message": "🧐 사용자님의 질문을 분석중입니다..."}, 
    )
    await asyncio.sleep(0.02)
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
    
    agent_spec, err = get_agent_spec(
        session=session,
        agent_id=body.agent.agent_id,
        agent_version=body.agent.agent_version,
        request_id=request_id,
    )
    if err:
        lg.logger.error(
f"""
Raises
---
위치: get_agent_spec
유저: {user_profile.username}
오류 메시지: {err}
---
"""     )
        yield await chunk(
            "error", 
            {"message": "❌ 서버 내부 오류가 발생하였습니다. 나중에 다시 시도해주세요."},
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
    simple_agent = AsyncSimpleAgent(
        provider=AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    )
    await asyncio.sleep(0.02)
    
    messages = [{"role": "system", "content": agent_spec.prompt}]
    messages.extend(history.marshal_to_messagelike(user))
    
    gen = simple_agent.astream_v2(
        messages=messages,
        deployment_id=body.llm.deployment_id
    )
    lg.logger.info(
f"""
---
📊 스트리밍을 시작합니다...
유저: {user_profile.username}
걸린 시간: {time.time() - start:.2f}초
---
"""
    )
    parts = ""
    async for response in gen:
        if response['type'] == 'delta':
            yield await chunk(
                event="data",
                data={"message": response['content']}
            )
            lg.logger.debug(f"Streaming: {response['content']}")
            parts += response['content']
        elif response['type'] == 'done':
            yield await chunk(
                event="done",
                data={"message": response['content']}
            )
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
        elif response['type'] == 'status':
            yield await chunk(
                event="status",
                data={"message": response['content']}
            )

        await asyncio.sleep(0.02)
    
    assistant = mdl.Message.assistant_message(
        message_id=assaistant_message_id,
        parent_message_id=user_message_id,
        content=mdl.Content(type='text', parts=[parts]),
        llm_deployment_id=body.llm.deployment_id
    )
    new_messages.append(assistant)
    lg.logger.info(
f"""
---
📦 결과 저장예정
유저: {user_profile.username}
걸린 시간: {time.time() - start:.2f}초
---
"""
    )
    err = set_history(
        session=session,
        history=history,
        new_messages=new_messages,
        request_id=request_id,   
        conversation_type='recommendation'
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
    
    err = _add_recommendation_conversation(
        session=session,
        recommendation_id=recommendation_id,
        agent_id=body.agent.agent_id,
        agent_version=body.agent.agent_version,
        conversation_id=body.conversation_id,
        user_message_id=user_message_id,
        assistant_message_id=assaistant_message_id
    )
    if err:
        lg.logger.error(
            f"Error setting recommendation for user {user_profile.user_id} in conversation {body.conversation_id}: {err}"
        )
        yield await chunk(
            "error", 
            {"message": "❌ Server sent error... Retry later."},
        )
        return
    

def get_conversation_id_by_recommendation(
    session: Session,
    request_id: str,
    user_profile: mdl.User,
    recommendation_id: str,
    params: mdl.GetConversationByRecommendationRequest
) -> Tuple[str, Exception | None]:
    """
    Get the conversation ID by recommendation ID.

    Args:
        session (Session): Database session dependency.
        request_id (str): The unique request ID for tracking.
        user_profile (mdl.User): The profile of the current user.
        recommendation_id (str): The ID of the recommendation.
        params (mdl.GetConversationByRecommendationRequest): Additional parameters for the request.

    Returns:
        Tuple[str, Exception | None]: The conversation ID and any error encountered.
    """
    RecommendationConversations = rec_tbl.RecommendationConversations

    stmt = (
        select(RecommendationConversations.conversation_id)
        .where(
            RecommendationConversations.recommendation_id == recommendation_id,
            RecommendationConversations.agent_id == params.agent_id,
            RecommendationConversations.agent_version == params.agent_version
        )
    )
    
    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    
    try:
        result = session.execute(stmt).scalars().all()
    except Exception as e:
        return "", e
    
    if len(result) == 0:
        return "", None

    return result[0], None




def delete_recommendation(
    session: Session,
    user_profile: mdl.User,
    request_id: str,
    recommendation_id: str
) -> Exception | None:
    """
    Delete a recommendation by its ID.

    Args:
        session (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.
        recommendation_id (str): The ID of the recommendation to delete.

    Returns:
        Exception | None: An error if the recommendation could not be deleted, otherwise None.
    """
    Recommendation = rec_tbl.Recommendation

    stmt = (
        update(Recommendation)
        .where(
            Recommendation.recommendation_id == recommendation_id,
            Recommendation.user_id == user_profile.user_id
        )
        .values(
            is_deleted=True,
            updated_at=dt.datetime.now()    
        )
    )
    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    try:
        session.execute(stmt)
        session.commit()
    except Exception as e:
        session.rollback()
        return e
    
    return None
    