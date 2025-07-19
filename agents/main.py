import os
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, create_model

from langchain.prompts import ChatPromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

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

# user= create_model(
#     "User",
#     user_id=(str, ...),
#     username=(str, ...),
#     email=(str, ...),
# )



class SimpleAgent:
    def __init__(
        self, 
        agent_id: str,
        version: str,
        messages: List[dict],
        issuer: str,
        model_name: str,
        deploy_version: str,
        output_schema: List[Attribute] | None = None
    ):
        self.agent_id = agent_id
        self.version = version
        
        self.issuer = issuer
        self.model_name = model_name
        self.deploy_version = deploy_version
        self.output_schema = output_schema
        
        if self.output_schema:
            parser = PydanticOutputParser(pydantic_object=self._to_pydantic_model())

        self.model: BaseChatModel = self._choose_model(issuer, deploy_version)
        self.prompt = ChatPromptTemplate(messages=messages)
        self.output_parser = parser if self.output_schema else None

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
    ):
        runnable = self.prompt | self.model 
        if self.output_parser:
            runnable = runnable | self.output_parser

        runnable.astream(
            {"user_input": "Your input here"},)

    def _to_pydantic_model(self) -> type[BaseModel]:

        kwargs = {}
        for attr in self.output_schema:
            kwargs[attr.attribute] = (eval(attr.type), Field(
                ...,
                description=f"{attr.attribute} of the output schema",
                examples=[f"example of {attr.attribute}"]
            ))

        Model = create_model(
            f"{self.model_name}",
            **kwargs,
        )
        return Model


    def _build_prompt(self, user_input: str) -> str:
        pass
    def _choose_model(
        self, 
        issuer: str, 
        deploy_version: str
    ) -> BaseChatModel:
        api_key = os.getenv(self.key_of_env)
        if not api_key:
            raise ValueError(f"API key for {issuer} is not set in environment variables.")

        match issuer:
            case "openai":
                return ChatOpenAI(
                    model=f"gpt-3.5-turbo-{deploy_version}",
                    api_key=api_key
                )
            case "anthropic":
                return ChatAnthropic(
                    model=f"claude-{deploy_version}",
                    api_key=api_key
                )
            case _:
                raise ValueError(f"Unsupported issuer: {issuer}")
