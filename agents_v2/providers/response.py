from typing import Generic
from pydantic import BaseModel

import agents_v2.types as t

class Usage(BaseModel):
    input_tokens: int
    output_tokens: int

class ProviderResponse(BaseModel, Generic[t.ResponseFormatT]):
    response: t.ResponseFormatT | None = None
    error: Exception | None = None
    usage: Usage | None = None