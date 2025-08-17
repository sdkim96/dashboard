import uuid
from typing import Annotated
from fastapi import UploadFile
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

import backend.constants as c
import backend.deps as dp
import backend.models as mdl
import backend.services.file as svc

FILES = APIRouter(
    prefix=c.APIPrefix.FILES.value,
    tags=[c.APITag.FILES],
)


@FILES.post(
    path="/upload", 
    summary="Upload File",
    description=""" 
## Retrieve a list of recommendations for the user.

This endpoint fetches a list of recommendations tailored for the user 
based on their profile and preferences. 
It returns a list of `RecommendationMaster` objects, each containing details about the recommendation such as title, description, creation date, and associated departments.

""",
    response_model=mdl.PostFileUploadResponse, 
)
async def upload_file(
    file: UploadFile,
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> mdl.PostFileUploadResponse:
    """
    Upload a file to the server.
    """

    file_id = "file-" + str(uuid.uuid4())
    filename = file.filename or "unknown.txt"
    file_size = file.size or -1
    file_content_type = file.content_type if file.content_type else "unknown"

    err = await svc.upload_file(
        file_id=file_id,
        filename=filename,
        file_size=file_size,
        file_content_type=file_content_type,
        file_stream=file.file,
        user_profile=user_profile,
        session=session,
    )
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Error uploading file: {err}"
        )

    return mdl.PostFileUploadResponse(
        status="success",
        message="File uploaded successfully.",
        request_id=request_id,
        file_id=file_id,
    )


@FILES.get(
    path="",
    summary="Get Files",
    response_model=mdl.GetFilesResponse,
    description="""

This endpoint allows users to retrieve a list of files they have uploaded to the server.
"""
)
async def get_files(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> mdl.GetFilesResponse:
    """
    Get a list of files uploaded by the user.
    """

    files, err = svc.get_files(user_profile=user_profile, session=session)
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving files: {err}"
        )

    return mdl.GetFilesResponse(
        status="success",
        message="Files retrieved successfully.",
        request_id=request_id,
        files=files,
    )


@FILES.post(
    path="/{file_id}/vectorize",
    summary="Vectorize Files",
    response_model=mdl.PostVectorizeFilesResponse,
    description="""
This endpoint allows users to vectorize their uploaded files.
"""
)
async def vectorize_files(
    file_id: str,
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> mdl.PostVectorizeFilesResponse:
    err = await svc.vectorize_file(
        request_id=request_id,
        user_profile=user_profile,
        session=session,
        file_id=file_id
    )
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Error vectorizing file: {err}"
        )

    return mdl.PostVectorizeFilesResponse(
        status="success",
        message="File vectorization started successfully.",
        request_id=request_id,
        file_id=file_id,
    )


@FILES.delete(
    path="/{file_id}",
    summary="Delete File",
    response_model=mdl.DeleteFilesByIDResponse,
    description="""
This endpoint allows users to delete their uploaded files.
"""
)
async def delete_file(
    file_id: str,
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
) -> mdl.DeleteFilesByIDResponse:
    err = await svc.delete_file(user_profile=user_profile, session=session, file_id=file_id)
    if err:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting file: {err}"
        )

    return mdl.DeleteFilesByIDResponse(
        status="success",
        message="File deleted successfully.",
        request_id=request_id,
        file_id=file_id
    )
