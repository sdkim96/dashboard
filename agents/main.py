import os
from typing import List, Optional, Tuple, Generic, TypeVar, cast

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

class SimpleChat:
    """
    A simple chat with no context
    """

    def __init__(self, agent: "AsyncSimpleAgent") -> None:
        self.agent = agent

    async def aquery(
        self,
        system_prompt: str,
        user_prompt: str,
        history: Optional[List[dict]] = [],
    ) -> Tuple[str, Exception | None]:
        """
        Creates a SimpleChat instance with the provided prompts and history.
        """
        messages = [
            {"role": "system", "content": system_prompt},
        ]
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": user_prompt})

        response, err = await self.agent.ainvoke(
            messages=messages,
            deployment_id="gpt-4o"
        )
        if err:
            return "", err
        return response, None


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
        output_schema: List[dict[str, str]] | None = None
    ):
        
        """
        Asynchronously streams the response from the agent based on the provided messages.

        Args:
            messages (List[dict]): The messages to send to the agent.
            output_schema (List[dict[str, str]] | None): The schema for the expected
                output. If None, the output will not be parsed.
        Yields:
            str: The response from the agent.
        """
        client = self.model
        chat = Chat(client)

        response_fmt: type[BaseModel] | None = None
        if output_schema:
            attributes = [Attribute.model_validate(s) for s in output_schema]
            response_fmt = self._to_pydantic_model(attributes)

        yield chat.astream(
            deployment_id=self.deployment_id,
            messages=messages,
            output_schema=response_fmt
        )

    def _to_pydantic_model(self, output_schema: List[Attribute]) -> type[BaseModel]:

        kwargs = {}
        for attr in output_schema:
            kwargs[attr.attribute] = (eval(attr.type), Field(
                ...,
                description=f"{attr.attribute} of the output schema",
                examples=[f"example of {attr.attribute}"]
            ))

        Model = create_model(
            f"OutputSchema",
            __base__=BaseModel,
            **kwargs,
        )
        return Model


    def _choose_model(
        self, 
        issuer: str, 
        deploy_version: str
    ):

        api_key = os.getenv(self.key_of_env)
        if not api_key:
            raise ValueError(f"API key for {issuer} is not set in environment variables.")

        match issuer:
            case "openai":
                return OpenAI(
                    api_key=api_key
                )
            case "anthropic":
                return Anthropic(
                    api_key=api_key
                )
            case _:
                raise ValueError(f"Unsupported issuer: {issuer}")
