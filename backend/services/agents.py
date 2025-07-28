import datetime as dt
import json
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

import backend.models as mdl

import backend.db.agent_tables as tbl
import backend.db.user_tables as user_tbl
import backend.utils.logger as lg


def get_available_agents(
    session: Session,
    request_id: str,
    user: mdl.User,
    offset: int,
    limit: int,
    search: Optional[str] = None,
) -> Tuple[List[mdl.AgentMarketPlace], Exception | None]:
    
    lg.logger.info(
        f"Request ID: {request_id}, Username: {user.username}, "
        f"Offset: {offset}, Limit: {limit}, Search: {search}"
    )
    
    Master = tbl.Agent
    Detail = tbl.AgentDetail
    Tag = tbl.AgentTag

    stmt = (
        select(
            Master.agent_id,
            Detail.version,
            Master.name,
            Detail.icon_link,
            func.array_agg(Tag.tag).label("tags"),
            Master.department_name,
        )
        .join(
            Detail,
            Master.agent_id == Detail.agent_id
        )
        .outerjoin(
            Tag,
            Master.agent_id == Tag.agent_id
        )
        .where(
            Detail.is_active.is_(True),
            Detail.is_deleted.is_(False),
        )
        .order_by(Detail.created_at.desc())
        .group_by(
            Master.agent_id,
            Detail.version,
            Master.name,
            Detail.icon_link,
            Detail.created_at,
            Master.department_name,
        )
    )

    if search:
        stmt = stmt.where(
            or_(
                Master.name.ilike(f"%{search}%"),
            )
        )

    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    try:
        results = session.execute(stmt).mappings().all()
    except Exception as e:
        return [], e

    agents = [
        mdl.AgentMarketPlace(
            agent_id=row.agent_id,
            agent_version=row.version,
            name=row.name,
            icon_link=row.icon_link,
            tags=row.tags or [],
            department_name=row.department_name,
        )
        for row in results
    ]

    return agents, None



def get_detail_by_agent_id(
    session: Session,
    request_id: str,
    username: str,
    agent_id: str,
    agent_version: int
) -> Tuple[mdl.AgentDetail, Exception | None]:
    
    lg.logger.info(
        f"Request ID: {request_id}, Username: {username}, "
        f"Looking for Agent ID: {agent_id}"
    )
    
    Master = tbl.Agent
    Detail = tbl.AgentDetail
    Tag = tbl.AgentTag
    User = user_tbl.User

    
    stmt = (
        select(
            Master.agent_id,
            Detail.version.label("agent_version"),
            Master.department_name,
            Master.name,
            Detail.description,
            func.array_agg(Tag.tag).label("tags"),
            Detail.icon_link,
            Detail.created_at,
            Detail.updated_at,
            User.username.label("author_name"),
        )
        .join(
            Detail,
            Master.agent_id == Detail.agent_id
        )
        .outerjoin(
            Tag,
            Master.agent_id == Tag.agent_id
        )
        .join(
            User,
            User.user_id == Master.author_id
        )
        .where(
            Master.agent_id == agent_id,
            Detail.is_active.is_(True),
            Detail.is_deleted.is_(False),
            Detail.version == agent_version,
        )
        .group_by(
            Master.agent_id,
            Detail.version,
            Master.department_name,
            Master.name,
            Detail.description,
            Detail.icon_link,
            Detail.created_at,
            Detail.updated_at,
            User.username,           
        )
    )
    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    try:
        result = session.execute(stmt).mappings().one_or_none()
        if not result:
            return mdl.AgentDetail.failed(), Exception("Agent not found")
    except Exception as e:
        lg.logger.error(f"Error retrieving agent details: {e}")
        return mdl.AgentDetail.failed(), e    
    
    try:
        validated = mdl.AgentDetail.model_validate(dict(result))
        return validated, None
    except Exception as e:
        lg.logger.error(f"Error validating agent detail: {e}")
        return mdl.AgentDetail.failed(), e


def publish_agent(
    session: Session,
    publish: mdl.AgentPublish,
    user_profile: mdl.User,
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
            updated_at=now,
            department_name=publish.department_name
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