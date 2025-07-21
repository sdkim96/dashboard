from typing import Annotated
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from sqlalchemy.orm import Session

import backend.services.completion as svc
import backend.constants as c
import backend.deps as dp
import backend.models.api as mdl

COMPLETION = APIRouter(
    prefix=c.APIPrefix.COMPLETION.value,
    tags=[c.APITag.COMPLETION],
)

@COMPLETION.post(
    path="",
    summary="Generate Completion",
    description="Generates a completion based on the provided input.",
    response_class=StreamingResponse,
    responses={
        200: {
            "description": "Streaming response containing the generated completion.",
            "content": {
                "text/event-stream": {
                    "schema": {
                        "type": "string",
                        "format": "event-stream",
                        "x-stream-type": "server-sent-events",
                    },
                    "example": "data: {\"message\": \"Generated text here...\"}\n\n"
                }
            }
        },
    },
    openapi_extra={
        "x-streaming": True,
        "x-stream-response": True,
        "x-response-format": "text/event-stream"
    }
)
async def generate_completion(
    request_id: Annotated[str, Depends(dp.generate_request_id)],
    session: Annotated[Session, Depends(dp.get_db)],
    user_profile: Annotated[mdl.User, Depends(dp.get_current_userprofile)],
    body: mdl.PostGenerateCompletionRequest
) -> StreamingResponse:
    """
    Generates a completion based on the input data.
    
    Args:
        input_data (dict): The input data for generating the completion.
        
    Returns:
        StreamingResponse: A streaming response containing the generated completion.
    """
    func = svc.chat_completion
    if body.action == "stop":
        return StreamingResponse(
            iter([]), 
            media_type="text/event-stream"
        )

    if body.action == "next":
        generator = func(
            session=session,
            request_id=request_id,
            user_profile=user_profile,
            body=body
        )

    return StreamingResponse(generator, media_type="text/event-stream")