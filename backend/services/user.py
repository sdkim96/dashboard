import datetime as dt
import json
import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select, or_, func
from sqlalchemy.orm import Session

import backend.models as mdl
import backend.db.conversations_tables as tbl
import backend.db.agent_tables as agent_tbl
import backend.utils.logger as lg

def get_me(
    session: Session,
    user_profile: mdl.User,
    request_id: str,
) -> Tuple[List[mdl.LLMModel], Exception | None]:
    """
    Retrieves the current user's information including agents and LLMs.

    Args:
        session (Session): Database session for querying user data.
        user_profile (mdl.User): Current user's profile information.
        request_id (str): Unique identifier for the request.

    Returns:
        Tuple[List[mdl.LLMModel], Exception | None]: List of agents, list of LLMs, and any error encountered.
    """
    llms = []
    LLM = tbl.LLMIssuer

    stmt = (
        select(
            LLM.deployment_id,
            LLM.issuer,
            LLM.name,
            LLM.description,
            LLM.icon_link
        )
    )
    lg.logger.debug(f"SQL Query: {stmt.compile(compile_kwargs={'literal_binds': True})}")
    try:
        result = session.execute(stmt).mappings().all()
    except Exception as e:
        lg.logger.error(f"Failed to retrieve user information: {e}", request_id=request_id)
        return llms, e

    for row in result:
        llms.append(
            mdl.LLMModel(
                issuer=row["issuer"],
                deployment_id=row["deployment_id"],
                name=row["name"],
                description=row["description"],
                icon_link=row["icon_link"]
            )
        )
    return llms, None