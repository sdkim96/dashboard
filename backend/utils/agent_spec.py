import json
from typing import Optional, Tuple, List, cast
from sqlalchemy import select
from sqlalchemy.orm import Session

import backend.db.agent_tables as tbl
import backend.models as mdl

def get_agent_spec(
    session: Session,
    agent_id: str,
    agent_version: int,
    request_id: str
) -> Tuple[mdl.AgentSpec, Exception | None]:
    
    """
    Retrieves the agent specification from the database.

    Args:
        session (Session): The database session.
        agent_id (str): The ID of the agent.
        request_id (str): The request ID for logging.

    Returns:
        Tuple[mdl.AgentDetail, Exception | None]: The agent specification and any error encountered.
    """
    AgentDetail = tbl.AgentDetail

    stmt = (
        select(AgentDetail)
        .where(AgentDetail.agent_id == agent_id)
        .where(AgentDetail.version == agent_version)
    )
    try:
        result = session.execute(stmt).scalar_one_or_none()
    except Exception as e:
        return mdl.AgentSpec.failed(), Exception(f"Agent with ID {agent_id} not found.: {e}")
    
    if result is None:
        return mdl.AgentSpec.failed(), Exception(f"Agent with ID {agent_id} not found.")
    
    if not result.output_schema:
        return mdl.AgentSpec.model_validate(result), None

    output_schema: List[mdl.Attribute] = []
    unmarshaled = cast(
        dict[str, str],
        json.loads(result.output_schema)
    )
    for attr, type in unmarshaled.items():
        output_schema.append(mdl.Attribute(attribute=attr, type=type))

    return mdl.AgentSpec(
        agent_id=result.agent_id,
        version=result.version,
        prompt=result.prompt,
        output_schema=output_schema
    ), None
    