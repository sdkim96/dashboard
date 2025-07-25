import datetime as dt
from typing import List, Optional, Tuple

from sqlalchemy import select, func, or_, literal
from sqlalchemy.orm import Session

import backend.db.tools_tables as tbl
import backend.db.user_tables as user_tbl
import backend.utils.logger as lg

from backend import models as mdl

def get_available_tools(
    session: Session,
    request_id: str,
    user_profile: mdl.User,
    offset: int,
    limit: int,
    search: Optional[str] = None,
) -> Tuple[List[mdl.ToolMaster], Exception | None]:
    
    lg.logger.info(
        f"Request ID: {request_id}, Username: {user_profile.username}, "
        f"Offset: {offset}, Limit: {limit}, Search: {search}"
    )
    
    Tool = tbl.Tool
    Subscriber = tbl.ToolSubscriber
    User = user_tbl.User

    stmt = (
        select(
            Tool.tool_id,
            Tool.tool_name,
            User.username.label("author_name"),
            Tool.icon_link,
            func.count(func.distinct(Subscriber.user_id)).label("subscriber_count"),
            Tool.created_at,
            Tool.updated_at,
            func.coalesce(
                func.bool_or(Subscriber.user_id == user_profile.user_id),
                False
            ).label("is_subscribed"),
        )
        .outerjoin(
            Subscriber,
            Tool.tool_id == Subscriber.tool_id
        )
        .outerjoin(
            User,
            Tool.author_id == User.user_id
        )
        .where(Tool.is_deleted == False)
        .group_by(
            Tool.tool_id,
            Tool.tool_name,
            User.username,
            Tool.icon_link,
            Tool.created_at,
            Tool.updated_at
        )
    )

    if search:
        stmt = stmt.where(
            or_(
                Tool.tool_name.ilike(f"%{search}%"),
            )
        )

    stmt = stmt.order_by(Tool.created_at.desc()).offset(offset).limit(limit)
    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    try:
        results = session.execute(stmt).mappings().all()
    except Exception as e:
        return [], e

    tools = [
        mdl.ToolMaster(
            tool_id=row.tool_id,
            tool_name=row.tool_name,
            author_name=row.author_name,
            icon_link=row.icon_link,
            subscriber_count=row.subscriber_count,
            created_at=row.created_at,
            updated_at=row.updated_at,
            is_subscribed=row.is_subscribed,
        )
        for row in results
    ]

    lg.logger.info(
        f"Retrieved {len(tools)} tools for user {user_profile.username} with request ID {request_id}."
    )
    return tools, None


def get_tool_by_id(
    session: Session,
    request_id: str,
    user_profile: mdl.User,
    tool_id: str,
) -> Tuple[mdl.Tool, Exception | None]:
    
    lg.logger.info(
        f"Request ID: {request_id}, Username: {user_profile.username}, Tool ID: {tool_id}"
    )
    
    Tool = tbl.Tool
    Subscriber = tbl.ToolSubscriber
    User = user_tbl.User

    subscriber_count_subq = (
        select(
            Subscriber.tool_id,
            func.count(Subscriber.user_id).label("subscriber_count")
        )
        .group_by(Subscriber.tool_id)
        .subquery()
    )

    user_subscription_subq = (
        select(
            Subscriber.tool_id,
            literal(True).label("is_subscribed")
        )
        .where(Subscriber.user_id == user_profile.user_id)

        .subquery()
    )

    
    stmt = (
        select(
            Tool.tool_id,
            Tool.tool_name,
            User.username.label("author_name"),
            Tool.icon_link,
            func.coalesce(subscriber_count_subq.c.subscriber_count, 0).label("subscriber_count"),
            Tool.created_at,
            Tool.updated_at,
            func.coalesce(user_subscription_subq.c.is_subscribed, False).label("is_subscribed"),
            Tool.description
        )
        .outerjoin(
            subscriber_count_subq,
            Tool.tool_id == subscriber_count_subq.c.tool_id
        )
        .outerjoin(
            User,
            Tool.author_id == User.user_id
        )
    )
    
    stmt = stmt.outerjoin(
        user_subscription_subq,
        Tool.tool_id == user_subscription_subq.c.tool_id
    )
    
    stmt = stmt.where(Tool.is_deleted == False).where(Tool.tool_id == tool_id)
    

    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    try:
        result = session.execute(stmt).mappings().one_or_none()
    except Exception as e:
        return mdl.Tool.failed(), e

    if not result:
        lg.logger.warning(f"Tool with ID {tool_id} not found for user {user_profile.username}.")
        return mdl.Tool.failed(), None

    tool = mdl.Tool(
        tool_id=result.tool_id,
        tool_name=result.tool_name,
        author_name=result.author_name,
        icon_link=result.icon_link,
        subscriber_count=result.subscriber_count,
        description=result.description,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )

    lg.logger.info(
        f"Retrieved tool {tool.tool_name} with ID {tool.tool_id} for user {user_profile.username} with request ID {request_id}."
    )
    return tool, None


def subscribe_tool(
    session: Session,
    request_id: str,
    user: mdl.User,
    tool_id: str,
) -> Tuple[bool, Exception | None]:
    
    lg.logger.info(
        f"Request ID: {request_id}, Username: {user.username}, Tool ID: {tool_id}"
    )
    
    Tool = tbl.Tool
    Subscriber = tbl.ToolSubscriber

    try:
        stmt = (
            select(Tool)
            .where(Tool.tool_id == tool_id, Tool.is_deleted == False)
        )
        tool = session.execute(stmt).scalar_one_or_none()
        
        if not tool:
            lg.logger.warning(f"Tool with ID {tool_id} not found for subscription.")
            return False, None
        
        new_subscription = Subscriber(
            tool_id=tool_id,
            user_id=user.user_id,
            created_at=dt.datetime.now()
        )
        
        session.add(new_subscription)
        session.commit()
        
        lg.logger.info(
            f"User {user.username} subscribed to tool {tool.tool_name} with ID {tool.tool_id}."
        )
        return True, None
    
    except Exception as e:
        session.rollback()
        lg.logger.error(f"Error subscribing to tool {tool_id}: {e}")
        return False, e