import uuid
from typing import List
from langchain_postgres import PGVector
from langchain_postgres import PGVectorStore

from pydantic import BaseModel, Field


class Document(BaseModel):

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()), 
        description="Unique identifier for the document."
    )
    content: str = Field(
        ..., 
        description="The content of the document."
    )
    metadata: dict = Field(
        ...,
        description="Metadata associated with the document."
    )

class VectorStore:


    def add_documents(
        self,
        documents: List[Document],
    ): ...


    def delete_by_ids(
        self,
        ids: List[str]
    ): ...

    async def search(
        self,
        query: str,
        top_k: int
    ) -> List[Document]: ...