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
    is_superuser: bool = Field(
        False,
        description="Flag indicating whether the user has superuser privileges.",
        examples=[True, False]
    )

    @classmethod
    def mock(cls) -> "User":
        """Create a mock user instance for testing."""
        return cls(
            user_id="user-123",
            username="example_user",
            email="example@gmail.com",
            icon_link="https://example.com/icon.png",
            is_superuser=False,
        )