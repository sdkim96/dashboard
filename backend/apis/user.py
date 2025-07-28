from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

import backend.constants as c
import backend.deps as dp
import backend.models.api as mdl

import backend.services.user as svc

USER = APIRouter(
    prefix=c.APIPrefix.USER.value,
    tags=[c.APITag.USER],
)

@USER.get(
    path="",
    summary="Get User Information",
    description="Retrieves information about the current user.",
    response_model=mdl.GetMeResponse,
)
def get_me(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> mdl.GetMeResponse:
    """
    Retrieves the current user's information.
    
    Args:
        request_id (str): Unique identifier for the request.
        session (Session): Database session for querying user data.
        user_profile (mdl.User): Current user's profile information.
        
    Returns:
        GetMeResponse: User information model.
    """
    llms, err = svc.get_me(
        session=session,
        user_profile=user_profile,
        request_id=request_id,
    )
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user information: {err}"
        )
    return mdl.GetMeResponse(
        status="success",
        message="User information retrieved successfully.",
        request_id=request_id,
        user=user_profile,
        llms=llms
    )
