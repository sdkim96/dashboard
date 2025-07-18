from pydantic import BaseModel, Field

class LLMModel(BaseModel):
    model_id: str = Field(
        ...,
        description="Unique identifier of the model.",
        examples=["user-123"]
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
    deployment_id: str = Field(
        ...,
        description="Deployment identifier for the model.",
        examples=["deployment-123"]
    )
    icon_link: str | None = Field(
        None,
        description="Link to the user's icon or avatar, if available.",
        examples=["https://example.com/icon.png"]
    )

