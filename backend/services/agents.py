import datetime as dt
import json
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

import backend.models.agent as a_mdl
import backend.models.user as u_mdl

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


def publish_agent(
    session: Session,
    publish: a_mdl.AgentPublish,
    user_profile: u_mdl.User,
    request_id: str,
) -> Tuple[bool, Exception | None]:
    """ Publishes a new agent to the database.
    Args:
        session (Session): SQLAlchemy session object.
        publish (a_mdl.AgentPublish): Agent details to be published.
        user_profile (u_mdl.User): Current user's profile.
        request_id (str): Unique request ID for tracking.
    
    Returns:
        out (Tuple[bool, Exception | None]): Returns True if successful, otherwise False and the exception
    
    """
    lg.logger.info(
        f"Request ID: {request_id}, Name: {publish.name}, Description: {publish.description}, "
        f"Icon Link: {publish.icon_link}, Tags: {publish.tags}, Prompt: {publish.prompt}"
    )
    now = dt.datetime.now()
    new = not publish.agent_id
    agent_id = publish.agent_id or "agent-" + str(uuid.uuid4())
    version = 0
    marshal_target = None

    if not new:
        stmt = (
            select(
                func.max(tbl.AgentDetail.version).label("max_version")
            ).where(
                tbl.AgentDetail.agent_id == publish.agent_id
            )
        )
        try:
            last_version = session.execute(stmt).scalar_one_or_none()
            owner = session.execute(
                select(tbl.Agent.author_id).where(
                    tbl.Agent.agent_id == publish.agent_id
                )
            ).scalar_one_or_none()
        except Exception as e:
            return False, e

        if last_version is None:
            return False, Exception("Agent not found")
        
        if owner != user_profile.user_id:
            return False, Exception("Not authorized to update this agent")
        
        version = last_version + 1

    if new:
        new_agent = tbl.Agent(
            agent_id=agent_id,
            author_id=user_profile.user_id,
            name=publish.name,
            icon_link=publish.icon_link,
            description=publish.description,
            is_deleted=False,
            is_active=True,
            created_at=now,
            updated_at=now
        )
        session.add(new_agent)
    
    if publish.output_schema:
        marshal_target = {}
        schema = publish.output_schema
        for attr in schema:
            marshal_target[attr.attribute] = attr.type
        
        marshal_target = json.dumps(marshal_target)

    detail = tbl.AgentDetail(
        agent_id=agent_id,
        version=version,
        prompt=publish.prompt,
        output_schema=marshal_target,
        created_at=now,
        updated_at=now
    )
    session.add(detail)

    for tag in publish.tags:
        new_tag = tbl.AgentTag(
            agent_id=agent_id,
            agent_version=version,
            tag=tag,
            created_at=now,
            updated_at=now
        )
        session.add(new_tag)

    try:
        session.commit()
    except Exception as e:
        session.rollback()
        return False, e

    return True, None