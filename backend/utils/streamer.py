import backend._types as t
import backend.models as mdl

async def chunk(event: str, data: t.CompletionChunkUnion) -> str:
    """
    Formats the event and data into a chunked string for streaming.

    Args:
        event (str): The event type.
        data (t.CompletionChunkUnion): The data to be sent. It can be a string, BaseModel, or dict.
        delay (float | None): Optional delay for the message.

    Returns:
        str: The formatted string for streaming.
    """
    completion = mdl.CompletionMessage(
        event=event,
        data=data,

    )
    buffer = await completion.to_stream()
    return buffer
    