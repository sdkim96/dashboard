import abc
from typing import Generic, TypeVar
from pydantic import BaseModel

class PydanticFormatType(BaseModel, abc.ABC):
    
    @abc.abstractmethod
    @classmethod
    def default(cls) -> "PydanticFormatType":
        pass

ResponseFormatT = TypeVar("ResponseFormatT", bound=PydanticFormatType | str)
