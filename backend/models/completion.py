import asyncio
import json
from typing import Annotated, Union
from pydantic import BaseModel, Field

import backend._types as t

class CompletionMessage(BaseModel):
    event: str = Field(
        ...,
        description="Event type for the completion message, e.g., 'message' or 'error'.",
        examples=["message", "error"]
    )
    data: Union[str, dict, BaseModel] = Field(
        ...,
        description="Data for the completion message, typically the generated text.",
        examples=["This is the generated text."]
    )
    delay: float = Field(
        ...,
        description="Delay for the message, if applicable.",
        examples=[0.01]
    )

    async def to_stream(self, delay: float | None = None) -> str:
        """
        Converts the message to a streaming format.

        Returns:
            str: The formatted string for streaming.
        """
        delay = delay or self.delay
        data = self.data
        sse = "event: {event}\ndata: {data}\n\n"
        
        await asyncio.sleep(delay)
        
        if isinstance(self.data, BaseModel):
            data = self.data.model_dump_json()
            return sse.format(event=self.event, data=data)
        
        if isinstance(self.data, dict):
            data = json.dumps(self.data, ensure_ascii=False)
            return sse.format(event=self.event, data=data)

        return sse.format(event=self.event, data=self.data)