from typing import List, Optional, Tuple

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

import backend.models.agent as a_mdl
import backend.db.agent_tables as tbl


def get_available_agents(
    session: Session,
    request_id: str,
    username: str,
    offset: int,
    limit: int,
    search: Optional[str] = None,
) -> Tuple[List[a_mdl.Agent], Exception | None]:
    
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
        results = session.execute(stmt).all()
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