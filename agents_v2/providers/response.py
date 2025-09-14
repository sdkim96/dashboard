from typing import Generic
from pydantic import BaseModel, ConfigDict

import agents_v2.types as t

class Usage(BaseModel):
    input_tokens: int
    output_tokens: int

class ProviderResponse(BaseModel, Generic[t.ResponseFormatT]):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    response: t.ResponseFormatT | None = None
    error: Exception | None = None
    usage: Usage | None = None