import datetime as dt
import uuid
from typing import (
    List,
    TypeVar, 
)

import elasticsearch.dsl as dsl

from pydantic import BaseModel, Field

class IndexFileMeta(dsl.InnerDoc):
    file_id = dsl.Keyword()
    file_path = dsl.Keyword()
    file_name = dsl.Keyword()
    file_extension = dsl.Keyword()
    file_type = dsl.Keyword()
    file_description = dsl.Text(analyzer="nori")
    effective_from = dsl.Date()
    effective_to = dsl.Date()
    author = dsl.Keyword()
    department = dsl.Keyword()

class IndexPageMeta(dsl.InnerDoc):
    number = dsl.Integer()
    total_pages = dsl.Integer()
    prev = dsl.Integer()
    next = dsl.Integer()

class Index(dsl.AsyncDocument):
    document_id = dsl.Keyword()
    content = dsl.Text(analyzer="nori")
    vector = dsl.DenseVector(dims=1536)
    tags = dsl.Keyword()
    page_meta = dsl.Object(IndexPageMeta)
    file_meta = dsl.Object(IndexFileMeta)
    created_at = dsl.Date()
    updated_at = dsl.Date()


class PageMeta(BaseModel):
    number: int = Field(
        ...,
        description="Page number of the document."
    )
    total_pages: int = Field(
        ...,
        description="Total number of pages in the document."
    )

    @property
    def prev(self) -> int:
        if self.number > 0:
            return self.number - 1
        return -1

    @property
    def next(self) -> int:
        if self.number < self.total_pages - 1:
            return self.number + 1
        return -1

    def to_es(self) -> IndexPageMeta:
        return IndexPageMeta(
            number=self.number, # type: ignore
            total_pages=self.total_pages, # type: ignore
            prev=self.prev, # type: ignore
            next=self.next   # type: ignore
        )

class FileMeta(BaseModel):

    file_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the file, typically a UUID."
    )
    file_path: str = Field(
        ...,
        description="Original file path of the uploaded document."
    )
    file_name: str = Field(
        ...,
        description="Original file name of the uploaded document."
    )
    file_extension: str = Field(
        default="",
        description="Original file extension of the uploaded document, can be empty."
    )
    file_type: str = Field(
        ...,
        description="Original file type of the uploaded document. (e.g., 'manual', 'report', 'invoice', etc.)"
    )
    file_description: str = Field(
        default="",
        description="Description of the file, can be empty."
    )
    effective_from: dt.datetime = Field(
        default_factory=dt.datetime.now,
        description="Effective date from which the file is valid."
    )
    effective_to: dt.datetime = Field(
        default_factory=lambda: dt.datetime(9999, 12, 31),
        description="Effective date until which the file is valid. Defaults to a far future date."
    )
    author: str = Field(
        default="",
        description="Author of the file, can be empty."
    )
    department: str = Field(
        default="",
        description="Department associated with the file, can be empty."
    )


    def to_es(self) -> IndexFileMeta:
        return IndexFileMeta(
            file_id=self.file_id, # type: ignore
            file_path=self.file_path, # type: ignore
            file_name=self.file_name, # type: ignore
            file_type=self.file_type, # type: ignore
            file_extension=self.file_extension, # type: ignore
            file_description=self.file_description, # type: ignore
            effective_from=self.effective_from, # type: ignore
            effective_to=self.effective_to, # type: ignore
            author=self.author, # type: ignore
            department=self.department # type: ignore
        )


class Document(BaseModel):
    document_id: str = Field(
        ...,
        description="Unique identifier for the document, typically a UUID."
    )
    content: str = Field(
        ...,
        description="The main content of the document, which will be indexed for search."
    )
    tags: List[str] = Field(
        ...,
        description="Tags associated with the document for categorization or filtering."
    )
    file_meta: FileMeta = Field(
        ...,
        description="Metadata associated with the document, such as user ID and file details."
    )
    page_meta: PageMeta = Field(
        ...,
        description="Metadata about the page, including page number and total pages."
    )
    created_at: dt.datetime = Field(
        default_factory=dt.datetime.now
    )
    updated_at: dt.datetime = Field(
        default_factory=dt.datetime.now
    )
    @classmethod
    def get_es_definition(cls) -> type[Index]:
        return Index

    def to_es(self, vector: List[float]) -> Index:

        return Index(
            document_id=self.document_id, # type: ignore
            content=self.content, # type: ignore
            vector=vector, # type: ignore
            tags=self.tags, # type: ignore
            page_meta=self.page_meta.to_es(), # type: ignore
            file_meta=self.file_meta.to_es(), # type: ignore
            created_at=self.created_at, # type: ignore
            updated_at=self.updated_at # type: ignore
        ) 

class SearchFilter(BaseModel):
    top_k: int = Field(
        default=10,
        description="Number of top results to return from the search."
    )
    stride_score: float = Field(
        default=0.5,
        lt=1.0,
        gt=0.0,
        description="Score threshold for filtering results based on stride. Default is 0.5."
    )
    effective_at: dt.datetime = Field(
        default_factory=dt.datetime.now,
        description="Effective date for the search, used to filter documents based on their effective period."
    )
    tags: List[str] = Field(
        default_factory=list,
        description="List of tags to filter the search results."
    )



DocumentT = TypeVar("DocumentT", bound="Document")