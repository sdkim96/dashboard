from typing import Literal, Generic, TypeVar

from pydantic import BaseModel

APIStatusLiteral = Literal['success', 'error']
DataUnion = dict | BaseModel | None

DataT = TypeVar('DataT', bound=DataUnion)

OutputSchemaLiteral = Literal['str', 'int', 'float', 'bool']
MessageRoleLiteral = Literal['user', 'assistant']
MessageContentType = Literal['text', 'image', 'file']
CompletionActionLiteral = Literal['next', 'retry', 'variant']