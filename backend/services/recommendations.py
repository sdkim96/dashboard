import os
import datetime as dt
import collections
import uuid
from typing import Tuple, List

from openai import AsyncOpenAI
from sqlalchemy import select, func
from sqlalchemy.orm import Session

import backend.db.agent_tables as tbl
import backend.models as mdl

from agents.main import SimpleChat, AsyncSimpleAgent
from agents.registry import AgentRegistry

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
            Master.description,
            Master.name,
            func.array_agg(Tags.tag).label("tags"),
            Master.icon_link,
            Master.created_at,
            Master.updated_at,
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
            Master.is_active.is_(True),
            Master.is_deleted.is_(False),
        )
        .group_by(
            Master.agent_id,
            Detail.version,
            Master.department_name,
            Master.description,
            Master.name,
            Master.icon_link,
            Master.created_at,
            Master.updated_at,
        )
    )
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
    

async def create_recommendation(
    session: Session,
    user_profile: mdl.User,
    body: mdl.PostRescommendationRequest,
    request_id: str
) -> Tuple[mdl.Recommendation, Exception | None]:
    """
    Create a new recommendation for the user.
    The process of creating a recommendation:
    1. Search the search engine 

    Args:
        session (Session): Database session dependency.
        user_profile (mdl.User): The profile of the current user.
        body (mdl.PostRescommendationRequest): The request body containing recommendation details.

    Returns:
        Tuple[mdl.Recommendation, Exception | None]: The created recommendation and any error encountered.
    """
    simple_agent = AsyncSimpleAgent(
        provider=AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
    )
    chat = SimpleChat(agent=simple_agent)
    context, err= await chat.aquery(
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
        ),
        user_prompt=body.work_details,
        history=[],
    )
    if err:
        return mdl.Recommendation.failed(), err
    
    agent_details, err = _get_agent_details(
        session=session,
    )
    if err:
        return mdl.Recommendation.failed(), err

    registry = AgentRegistry(
        agent_cards=[agent.model_dump(mode="json") for agent in agent_details],
    )
    search_results, err = await registry.asearch_by_ai(
        "최적의 AI 에이전트를 추천해줘. 이유와 점수와 함께.",
        context=context,
        search_engine=simple_agent
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
    
    return mdl.Recommendation(
        recommendation_id="rec-" + str(uuid.uuid4()),
        work_when = dt.datetime.now(),
        work_where= "Notion",
        work_whom="",
        work_details=body.work_details,
        agents=results
    ), None

    

    