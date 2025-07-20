import os
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, create_model
from anthropic import Anthropic
from openai import OpenAI

from agents.provider import Chat

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


class SimpleAgent:
    def __init__(
        self, 
        agent_id: str,
        agent_version: int,
        issuer: str,
        deployment_id: str,
    ):
        self.agent_id = agent_id
        self.version = agent_version
        
        self.issuer = issuer
        self.deployment_id = deployment_id

    @property
    def model(self) -> OpenAI | Anthropic:
        """
        Returns the model used by the agent.
        """
        return self._choose_model(self.issuer, self.deployment_id)

    @property
    def key_of_env(self) -> str:
        match self.issuer:
            case "openai":
                return "OPENAI_API_KEY"
            case "anthropic":
                return "ANTHROPIC_API_KEY"
            case _:
                raise ValueError(f"Unsupported issuer: {self.issuer}")

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

        yield await chat.ainvoke(
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
