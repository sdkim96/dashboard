from pydantic import BaseModel, Field

class User(BaseModel):
    user_id: str = Field(
        ...,
        description="Unique identifier of the user.",
        examples=["user-123"]
    )
    username: str = Field(
        ...,
        description="Username of the user.",
        examples=["example_user"]
    )
    email: str | None = Field(
        None,
        description="Email address of the user, if available.",
        examples=["example@gmail.com"]
    )
    icon_link: str | None = Field(
        None,
        description="Link to the user's icon or avatar, if available.",
        examples=["https://example.com/icon.png"]
    )