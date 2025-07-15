from typing import Generic

from pydantic import BaseModel, Field

import backend._types as t
import backend.constants as c

class BaseResponse(BaseModel):
    """
    Base response model for API responses.
    """
    status: t.APIStatusLiteral = Field(
        default='success', 
        description="Status of the response, e.g., 'success' or 'error'.",
        examples=["success", "error"]
    )
    message: str = Field(
        default=c.API_BASE_MESSAGE, 
        description="Message providing additional information about the response.",
        examples=[c.API_BASE_MESSAGE]
    )
    data: t.DataUnion = Field(
        default=None,
        description="Data returned by the API. Can be a dictionary, a Pydantic model, or None.",
        examples=[{"key": "value"}, None]
    )
    