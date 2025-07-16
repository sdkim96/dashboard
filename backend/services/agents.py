from typing import List, Optional, Tuple

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

import backend.models.agent as a_mdl
import backend.db.agent_tables as tbl
import backend.db.user_tables as user_tbl
import backend.utils.logger as lg


def get_available_agents(
    session: Session,
    request_id: str,
    username: str,
    offset: int,
    limit: int,
    search: Optional[str] = None,
) -> Tuple[List[a_mdl.Agent], Exception | None]:
    
    lg.logger.info(
        f"Request ID: {request_id}, Username: {username}, "
        f"Offset: {offset}, Limit: {limit}, Search: {search}"
    )
    
    Master = tbl.Agent
    Tag = tbl.AgentTag

    tag_subq = (
        select(
            Tag.agent_id,
            func.array_agg(Tag.tag).label("tags")
        )
        .group_by(Tag.agent_id)
        .subquery()
    )

    stmt = (
        select(
            Master.agent_id,
            Master.name,
            Master.icon_link,
            tag_subq.c.tags
        )
        .outerjoin(tag_subq, Master.agent_id == tag_subq.c.agent_id)
        .where(Master.is_active.is_(True), Master.is_deleted.is_(False))
    )

    if search:
        stmt = stmt.where(
            or_(
                Master.name.ilike(f"%{search}%"),
                func.array_to_string(tag_subq.c.tags, ' ').ilike(f"%{search}%")
            )
        )

    stmt = stmt.order_by(Master.created_at.desc()).offset(offset).limit(limit)

    try:
        results = session.execute(stmt).mappings().all()
    except Exception as e:
        return [], e

    agents = [
        a_mdl.Agent(
            agent_id=row.agent_id,
            name=row.name,
            icon_link=row.icon_link,
            tags=row.tags or []
        )
        for row in results
    ]

    return agents, None




def get_detail_by_agent_id(
    session: Session,
    request_id: str,
    username: str,
    agent_id: str,
) -> Tuple[a_mdl.AgentDetail, Exception | None]:
    
    lg.logger.info(
        f"Request ID: {request_id}, Username: {username}, "
        f"Looking for Agent ID: {agent_id}"
    )
    
    Master = tbl.Agent
    Detail = tbl.AgentDetail
    Tag = tbl.AgentTag
    Subcribe = tbl.AgentSubscriber
    Privacy = tbl.AgentPrivacy
    User = user_tbl.User

    
    stmt = (
        select(
            Master.agent_id,
            Master.author_id,
            Master.name,
            Master.description,
            Master.icon_link,
            func.array_agg(Tag.tag).label("tags"),
            Detail.prompt,
            Master.created_at,
            Master.updated_at
        )
        .join(Master, Master.agent_id == Detail.agent_id)
        .outerjoin(Tag, Master.agent_id == Tag.agent_id)
        .outerjoin(Subcribe, Subcribe.agent_id == Master.agent_id)
        .where(
            Master.agent_id == agent_id,
            Master.is_active.is_(True),
            Master.is_deleted.is_(False)
        )
        
    )


    