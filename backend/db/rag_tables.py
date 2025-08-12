import datetime as dt
from typing import Optional

from sqlalchemy import Engine, Index
from sqlalchemy.orm import mapped_column, DeclarativeBase, Mapped

class RAGBase(DeclarativeBase):
    pass

class File(RAGBase):
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
    effective_from: Mapped[dt.datetime] = mapped_column(
        default=dt.datetime.now,
        doc="The timestamp when the file became effective in the system."
    )
    effective_to: Mapped[dt.datetime] = mapped_column(
        default=None,
        doc="The timestamp when the file is no longer effective. It can be None if the file is currently effective."
    )
    author_id: Mapped[str] = mapped_column(
        doc="The ID of the user who uploaded the file. It is a foreign key to the user table."
    )
    department_name: Mapped[str] = mapped_column(
        doc="The department associated with the file. It is used to categorize files by department."
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
    

class Document(RAGBase):
    __tablename__ = 'document'

    document_id: Mapped[str] = mapped_column(
        primary_key=True,
        doc="A unique identifier for the document."
    )
    file_id: Mapped[str] = mapped_column(
        doc="Foreign key referencing the file this document belongs to."
    )

def create_rag_all(engine: Engine):
    RAGBase.metadata.create_all(engine)

def drop_rag_all(engine: Engine):
    RAGBase.metadata.drop_all(engine)