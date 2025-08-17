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
    User = user_tbl.User

    stmt = (
        select(
            Tool.tool_id,
            Tool.tool_name,
            User.username.label("author_name"),
            Tool.icon_link,
            Tool.created_at,
            Tool.updated_at,
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
            created_at=row.created_at,
            updated_at=row.updated_at,
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
    User = user_tbl.User
    
    stmt = (
        select(
            Tool.tool_id,
            Tool.tool_name,
            User.username.label("author_name"),
            Tool.icon_link,
            Tool.created_at,
            Tool.updated_at,
            Tool.description,
        )
        .join(User, Tool.author_id == User.user_id)
        .where(
            Tool.is_deleted == False,
            Tool.tool_id == tool_id
        )
    )

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
        description=result.description,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )

    lg.logger.info(
        f"Retrieved tool {tool.tool_name} with ID {tool.tool_id} for user {user_profile.username} with request ID {request_id}."
    )
    return tool, None



def get_tools_by_ids(
    session: Session,
    tool_ids: List[str],
) -> Tuple[List[mdl.Tool], Exception | None]:

    Tool = tbl.Tool
    User = user_tbl.User

    stmt = (
        select(
            Tool.tool_id,
            Tool.tool_name,
            Tool.description,
            User.username.label("author_name"),
            Tool.icon_link,
            Tool.created_at,
            Tool.updated_at,
        )
        .join(User, Tool.author_id == User.user_id)
        .where(Tool.tool_id.in_(tool_ids))
    )
    try:
        result = session.execute(stmt).mappings().all()
    except Exception as e:
        return [mdl.Tool.failed()], Exception(f"Tool with ID {tool_ids} not found.: {e}")

    tools = [mdl.Tool.model_validate(tool) for tool in result]

    return tools, None