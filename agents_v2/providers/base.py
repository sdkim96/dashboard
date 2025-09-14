from abc import ABC, abstractmethod
from enum import Enum

import agents_v2.types as t
from agents_v2.providers.response import ProviderResponse

class BaseProvider(ABC):

    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def ainvoke(
        self,
        *,
        instructions: str,
        prompt: str,
        history: list | None,
        model: Enum,
        response_fmt: type[t.ResponseFormatT],
    ) -> ProviderResponse[t.ResponseFormatT]:
        pass

    @abstractmethod
    async def astream(self):
        pass

