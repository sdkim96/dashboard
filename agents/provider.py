from typing import List, Optional, Generic, TypeVar, cast

from pydantic import BaseModel
from anthropic import Anthropic
from openai import OpenAI

ProviderT = TypeVar("ProviderT", Anthropic, OpenAI)
ParsedT = TypeVar("ParsedT", bound=BaseModel)

class Chat(Generic[ProviderT]):

    def __init__(
        self,
        client: ProviderT
    ) -> None:
        self.client = client

        if isinstance(client, OpenAI):
            self._create = client.chat.completions.create
            self._parse = client.chat.completions.parse
        elif isinstance(client, Anthropic):
            self._create = client.messages.create
            self._parse = self._parse_anthropic
        

    def _parse_anthropic(self, messages: List[dict], stream: bool = False):
        pass

    async def ainvoke(
        self,
        deployment_id: str,
        messages: List[dict],
        output_schema: ParsedT | None = None
    ) -> ParsedT | str:
        """
        Asynchronously invokes the chat model with the provided messages.
        
        Args:
            messages (List[dict]): The messages to send to the chat model.
            output_schema (ParsedT): The schema for the expected output.

        Returns:
            str: The response from the chat model.
        """
        if output_schema:
            parsed = self._parse(
                model=deployment_id,
                messages=messages,
                response_format=output_schema
            )
            if parsed:
                return parsed.choices[0].message.parsed

        return self._create(
            model=deployment_id,
            messages=messages,
        ).choices[0].message.content

    async def astream(
        self, 
        deployment_id: str,
        messages: list[dict], 
        output_schema: type[BaseModel] | None = None
    ):
        """
        Asynchronously streams responses from the chat model based on the provided messages.
        
        Args:
            deployment_id (str): The ID of the chat model to use.
            messages (list[dict]): The messages to send to the chat model.
            output_schema (list[dict], optional): The schema for the expected output.
        
        Yields:
            dict: The response from the chat model.
        """
        if output_schema:
            raise NotImplementedError(
                "Streaming with output schema is not implemented yet."
            )

        if isinstance(self.client, OpenAI):
            with self.client.chat.completions.stream(
                model=deployment_id,
                messages=messages,
            ) as stream:
                for event in stream:
                    match event.type:
                        case "content.delta":
                            yield {"event": "content.delta", "data": event.delta}
                        case "content.done":
                            yield {"event": "content.done", "data": event.content}
