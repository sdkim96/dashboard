from typing import Literal, Generic, TypeVar, Union

from pydantic import BaseModel

APIStatusLiteral = Literal['success', 'error']
DataUnion = dict | BaseModel | None

DataT = TypeVar('DataT', bound=DataUnion)

CompletionChunkUnion = Union[str, dict, BaseModel]
CompletionChunkT = TypeVar('CompletionChunkT', bound=CompletionChunkUnion)

OutputSchemaLiteral = Literal['str', 'int', 'float', 'bool']
MessageRoleLiteral = Literal['user', 'assistant']
MessageContentType = Literal['text', 'image', 'file']
CompletionActionLiteral = Literal['next', 'retry', 'variant']

DepartmentsLiteral = Literal[
    'Common',
    'HR',
    'Sales',
    'Marketing',
    'CustomerSupport',
    'Finance',
    'Planning',
    'BusinessSupport',
    'ProductDevelopment',
    'InternationalSales'
]