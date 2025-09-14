import abc
from typing import Generic, TypeVar
from pydantic import BaseModel

ToolOutputT = TypeVar("ToolOutputT")

class PydanticFormatType(BaseModel, abc.ABC):
    
    
    @classmethod
    @abc.abstractmethod
    def default(cls) -> "PydanticFormatType":
        pass

ResponseFormatT = TypeVar("ResponseFormatT", bound=PydanticFormatType | str)
