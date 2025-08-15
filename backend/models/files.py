import datetime as dt
from pydantic import BaseModel, Field, ConfigDict

class File(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )
    file_id: str = Field(
        ...,
        description="Unique identifier of the file.",
        examples=["file-12345"]
    )
    file_path: str = Field(
        ...,
        description="Path to the file.",
        examples=["/path/to/file.txt"]
    )
    file_name: str = Field(
        ...,
        description="Name of the file.",
        examples=["file"]
    )
    file_size: int = Field(
        ...,
        description="Size of the file in bytes.",
        examples=[1024]
    )
    file_extension: str = Field(
        ...,
        description="Extension of the file.",
        examples=["txt", "pdf", "jpg"]
    )
    file_content_type: str = Field(
        ...,
        description="Content type of the file.",
        examples=["text/plain", "application/pdf", "image/jpeg"]
    )
    author_id: str = Field(
        ...,
        description="ID of the user who uploaded the file.",
        examples=["user-12345"]
    )
    created_at: dt.datetime = Field(
        default=dt.datetime.now(),
        description="Timestamp when the file was created.",
        examples=[dt.datetime.now()]
    )
    updated_at: dt.datetime = Field(
        default=dt.datetime.now(),
        description="Timestamp when the file was last updated.",
        examples=[dt.datetime.now()]
    )

    @classmethod
    def failed(cls) -> "File":
        return cls(
            file_id="file-12345",
            file_path="/path/to/file.txt",
            file_name="file.txt",
            file_size=1024,
            file_extension="txt",
            file_content_type="text/plain",
            author_id="user-12345",
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now()
        )

    @classmethod
    def mock(cls) -> "File":
        return cls(
            file_id="file-12345",
            file_path="/path/to/file.txt",
            file_name="file.txt",
            file_size=1024,
            file_extension="txt",
            file_content_type="text/plain",
            author_id="user-12345",
            created_at=dt.datetime.now(),
            updated_at=dt.datetime.now()
        )