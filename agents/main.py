from typing import List,  Tuple, Generic, TypeVar, cast

from pydantic import BaseModel, Field, ConfigDict, create_model
from anthropic import Anthropic, AsyncAnthropic
from openai import AsyncOpenAI, OpenAI
from openai.types.chat import ChatCompletion

from agents.internal.search_engine import BaseSearchEngine

ProviderT = TypeVar("ProviderT", bound=OpenAI | Anthropic)
AsyncProviderT = TypeVar("AsyncProviderT", bound=AsyncOpenAI | AsyncAnthropic)

ParsedT = TypeVar("ParsedT", bound=BaseModel)

class Attribute(BaseModel):
    """
    Represents an attribute for the output schema of an agent's response.
    """
    attribute: str = Field(
        ...,
        description="attribute for the output schema",
        examples=["field1", "field2"]
    )
    type: str = Field(
        ...,
        description="type of the output schema, e.g., 'str', 'int', 'float', 'bool'.",
        examples=['str', 'int', 'float', 'bool']
    )

class AsyncSimpleAgent(Generic[AsyncProviderT]):
    def __init__(
        self, 
        provider: AsyncProviderT,
    ):
        
        self.provider = provider
        

    async def ainvoke(
        self,
        messages: List[dict],
        deployment_id: str,
    ) -> Tuple[str, Exception | None]:
        """
        Asynchronously invokes the agent with the provided messages and output schema.

        Args:
            messages (List[dict]): The messages to send to the agent.
            deployment_id (str): The ID of the agent's deployment.
        Returns:
            str: The response from the agent.
        """

        if isinstance(self.provider, AsyncOpenAI):
            try:
                result = cast(
                    ChatCompletion,
                    await self.provider.chat.completions.create(
                        model=deployment_id,
                        messages=messages,  # type: ignore
                    )
                )
            except Exception as e:
                return "", e
            try:
                cnt = result.choices[0].message.content
                if cnt is None:
                    return "", ValueError("No content in the response.")
                return cnt, None
            except Exception as e:
                return "", e

        elif isinstance(self.provider, AsyncAnthropic):
            raise NotImplementedError("AsyncAnthropic is not implemented yet.")

        return "", ValueError("Unsupported provider type.")


    async def aparse(
        self,
        messages: List[dict],
        response_fmt: type[ParsedT],
        deployment_id: str
    ) -> Tuple[ParsedT | None, Exception | None]:
        """
        Asynchronously parses the response from the agent based on the provided messages.

        Args:
            messages (List[dict]): The messages to send to the agent.
            output_schema (List[dict[str, str]] | None): The schema for the expected
                output. If None, the output will not be parsed.
        Returns:
            List[dict[str, str]]: The parsed response from the agent.
        """
        if isinstance(self.provider, AsyncOpenAI):
            response = await self.provider.chat.completions.parse(
                model=deployment_id,
                messages=messages, #type: ignore
                response_format=response_fmt
            )
        else:
            raise NotImplementedError("Parsing is not implemented for this provider.")
        
        parsed = response.choices[0].message.parsed
        if not parsed:
            return None, ValueError("No parsed content in the response.")

        return parsed, None

    
    async def astream(
        self,        
        messages: List[dict],
        deployment_id: str,
    ):
        
        """
        Asynchronously streams the response from the agent based on the provided messages.

        Args:
            messages (List[dict]): The messages to send to the agent.
            deployment_id (str): The ID of the agent's deployment.
        Yields:
            dict[str, str]: The response from the agent.
        
        Yield example:
            {'type': 'delta', 'content': event.delta}
            {'type': 'done', 'content': event.content}
            {'type': 'error', 'content': str(e)}
        """
        if isinstance(self.provider, AsyncOpenAI):
            try:
                async with self.provider.chat.completions.stream(
                    model=deployment_id,
                    messages=messages,  # type: ignore
                ) as stream:
                    async for event in stream:
                        if event.type == 'content.delta':
                            yield {'type': 'delta', 'content': event.delta}
                        elif event.type == 'content.done':
                            yield {'type': 'done', 'content': event.content}
            except Exception as e:
                yield {'type': 'error', 'content': str(e)}

        else:
            raise NotImplementedError("Streaming is not implemented for this provider.")

    
