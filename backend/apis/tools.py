import datetime as dt
import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from sqlalchemy.orm import Session

import backend.constants as c
import backend.deps as dp
import backend.models as mdl
import backend.services.tools as svc

TOOLS = APIRouter(
    prefix=c.APIPrefix.TOOLS.value,
    tags=[c.APITag.TOOLS],
)

@TOOLS.get(
    path="",
    summary="Get Tools",
    description="""
## Retrieves all available tools.

This API endpoint retrieves a list of all tools available in the system.
It does not require any parameters and returns a list of tools with their details.
    
""",
    response_model=mdl.GetToolsResponse,
)
def get_tools(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    params: mdl.GetToolsRequest = Depends(),
) -> mdl.GetToolsResponse:
    
    toolmasters, err = svc.get_available_tools(
        session=session,
        request_id=request_id,
        user_profile=user_profile,
        offset=params.offset,
        limit=params.size,
        search=params.search,
    )
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving tools: {err}"
        )
    
    return mdl.GetToolsResponse(
        status="success",
        message="Tools retrieved successfully.",
        request_id=request_id,
        tools=toolmasters,
        total=len(toolmasters),
        page=params.page,
        size=params.size,
        has_next=len(toolmasters) > params.size
    )



@TOOLS.get(
    path="/{tool_id}",
    summary="Get Tool by ID",
    description="""
## Retrieves a tool by its ID.

This API endpoint retrieves a tool by its unique identifier (ID).
It requires the tool ID as a path parameter and returns the tool's details.

""",
    response_model=mdl.GetToolByIDResponse,
)
def get_tool_by_id(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    tool_id: str,
) -> mdl.GetToolByIDResponse:

    tool, err = svc.get_tool_by_id(
        session=session,
        request_id=request_id,
        user_profile=user_profile,
        tool_id=tool_id,
    )

    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving tool: {err}"
        )

    return mdl.GetToolByIDResponse(
        status="success",
        message="Tools retrieved successfully.",
        request_id=request_id,
        tool=tool,
    )