import datetime as dt
import json
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

import backend.models as mdl
import backend.db.user_tables as user_tbl
import backend.db.agent_tables as agent_tbl
import backend.utils.logger as lg

def get_me(
    session: Session,
    user_profile: mdl.User,
    request_id: str,
) -> Tuple[List[mdl.Agent], List[mdl.LLMModel], Exception | None]:
    """
    Retrieves the current user's information including agents and LLMs.

    Args:
        session (Session): Database session for querying user data.
        user_profile (mdl.User): Current user's profile information.
        request_id (str): Unique identifier for the request.

    Returns:
        Tuple[List[mdl.Agent], List[mdl.LLMModel], Exception | None]: List of agents, list of LLMs, and any error encountered.
    """
    agents = []
    llms = [
        mdl.LLMModel(
            issuer="openai",
            deployment_id="gpt-4o-mini",
            name="GPT-4o Mini",
            description="A smaller version of GPT-4o, optimized for performance.",
            icon_link="https://example.com/gpt-4o-mini-icon.png"
        )
    ]

    Agent = agent_tbl.Agent
    AgentDetail = agent_tbl.AgentDetail
    AgentTag = agent_tbl.AgentTag
    AgentSubscriber = agent_tbl.AgentSubscriber

    stmt = (
        select(
            Agent.agent_id,
            AgentDetail.version.label("agent_version"),
            Agent.name,
            func.array_agg(AgentTag.tag).label("tags"),
            Agent.icon_link,
        )
        .join(
            AgentDetail,
            Agent.agent_id == AgentDetail.agent_id
        )
        .outerjoin(
            AgentTag,
            AgentTag.agent_id == Agent.agent_id
        )
        .join(
            AgentSubscriber,
            (AgentSubscriber.agent_id == Agent.agent_id) & 
            (AgentSubscriber.agent_version == AgentDetail.version)
        )
        .where(
            AgentSubscriber.user_id == user_profile.user_id
        )
        .group_by(
            Agent.agent_id,
            AgentDetail.version,
            Agent.name,
            Agent.icon_link,
        )
    )
    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    try:
        result = session.execute(stmt).mappings().all()        
    except Exception as e:
        lg.logger.error(f"Failed to retrieve user information: {e}", request_id=request_id)
        return agents, llms, e

    for row in result:
        agents.append(
            mdl.Agent(
                agent_id=row["agent_id"],
                name=row["name"],
                icon_link=row["icon_link"],
                tags=row["tags"] or [],
                agent_version=row["agent_version"],
            )
        )
    return agents, llms, None