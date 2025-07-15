from typing import Literal, Generic, TypeVar

from pydantic import BaseModel

APIStatusLiteral = Literal['success', 'error']
DataUnion = dict | BaseModel | None

DataT = TypeVar('DataT', bound=DataUnion)