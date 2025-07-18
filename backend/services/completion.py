from sqlalchemy.orm import Session

import backend._types as t
import backend.models as mdl

async def chunk(event: str, data: t.CompletionChunkUnion, delay: float | None) -> str:
    """
    Formats the event and data into a chunked string for streaming.

    Args:
        event (str): The event type.
        data (t.CompletionChunkUnion): The data to be sent. It can be a string, BaseModel, or dict.
        delay (float | None): Optional delay for the message.

    Returns:
        str: The formatted string for streaming.
    """
    delay = delay or 0.01
    completion = mdl.CompletionMessage(
        event=event,
        data=data,
        delay=delay
    )

    return await completion.to_stream()

async def chat_completion(
    session: Session,
    request_id: str,
    body: mdl.PostGenerateCompletionRequest
):
    history = await aget_history(
        session=session,
        request_id=request_id,
        conversation_id=body.conversation_id
    )
    yield await chunk(
        event="start", 
        data={"gene": "ss"}, 
        delay=0.01
    )
    yield await chunk("start", "Generating completion...", 0.01)
    await aset_history(
        session=session,
        request_id=request_id,
        conversation_id=body.conversation_id,
        content=body.content
    )