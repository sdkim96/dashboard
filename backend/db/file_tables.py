import datetime as dt
from typing import Optional

from sqlalchemy import Engine, Index
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

class FileBase(DeclarativeBase):
    pass

class File(FileBase):
    __tablename__ = 'file'

    file_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier for the document."
    )
    file_path: Mapped[str] = mapped_column(
        doc="The original file path of the uploaded document."
    )
    file_name: Mapped[str] = mapped_column(
        doc="The name of the file, typically the original name of the uploaded document."
    )
    file_size: Mapped[int] = mapped_column(
        doc="The size of the file in bytes."
    )
    file_extension: Mapped[str] = mapped_column(
        doc="The file extension of the document, e.g., 'pdf', 'docx'."
    )
    file_content_type: Mapped[str] = mapped_column(
        doc="The MIME type of the file, e.g., 'application/pdf', 'text/plain'."
    )
    author_id: Mapped[str] = mapped_column(
        doc="The ID of the user who uploaded the file. It is a foreign key to the user table."
    )
    is_deleted: Mapped[bool] = mapped_column(
        default=False,
        doc="Flag indicating whether the file is deleted. Default is False."
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        default=dt.datetime.now,
        doc="The timestamp when the file was created in the system."
    )
    updated_at: Mapped[dt.datetime] = mapped_column(
        default=None,
        doc="The timestamp when the file was last updated. It can be None if not updated."
    )
    

class Document(FileBase):
    __tablename__ = 'document'

    document_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier for the document."
    )
    file_id: Mapped[str] = mapped_column(
        doc="Foreign key referencing the file this document belongs to."
    )

class VectorizingFile(FileBase):
    __tablename__ = 'vectorizing_file'

    vectorizing_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier for the vectorized file."
    )
    file_id: Mapped[str] = mapped_column(
        doc="Foreign key referencing the file this vectorized document belongs to."
    )
    status: Mapped[str] = mapped_column(
        doc="The status of the vectorization process, e.g., 'red', 'yellow', 'green'."
    )
    error_message: Mapped[Optional[str]] = mapped_column(
        default=None,
        doc="An optional error message if the vectorization process fails."
    )
    created_at: Mapped[dt.datetime] = mapped_column(
        default=dt.datetime.now,
        doc="The timestamp when the vectorization process was initiated."
    )

def create_file_all(engine: Engine):
    FileBase.metadata.create_all(engine)

def drop_file_all(engine: Engine):
    FileBase.metadata.drop_all(engine)