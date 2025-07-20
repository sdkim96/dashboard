from pydantic import BaseModel, Field


class LLMModel(BaseModel):
    issuer: str = Field(
        ...,
        description="The issuer of the LLM model, e.g., 'openai', 'anthropic'.",
        examples=["openai", "anthropic"]
    )
    deployment_id: str = Field(
        ...,
        description="Deployment identifier for the model.",
        examples=["deployment-123"]
    )
    name: str = Field(
        ...,
        description="Username of the user.",
        examples=["example_user"]
    )
    description: str = Field(
        ...,
        description="Description of the model, if available.",
        examples=["This is an example model."]
    )
    
    icon_link: str | None = Field(
        None,
        description="Link to the user's icon or avatar, if available.",
        examples=["https://example.com/icon.png"]
        )

class LLMModelResponse(LLMModel):
    """
    Response model for LLM model operations.
    """
    pass
    


class LLMModelRequest(BaseModel):
    """
    Request model for LLM model operations.
    """
    issuer: str = Field(
        ...,
        description="The issuer of the LLM model, e.g., 'openai', 'anthropic'.",
        examples=["openai", "anthropic"]
    )
    deployment_id: str = Field(
        ...,
        description="Deployment identifier for the model.",
        examples=["deployment-123"]
    )
