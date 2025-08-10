import datetime as dt
import uuid
from typing import (
    List, 
    TypeVar, 
    Generic,
    Any
)

import elasticsearch.dsl as dsl

from elasticsearch import AsyncElasticsearch
from openai import AsyncOpenAI
from pydantic import BaseModel, Field


class IndexMetadata(dsl.InnerDoc):
    user_id = dsl.Keyword()
    original_file_path = dsl.Keyword()
    original_file_name = dsl.Keyword()
    original_file_size = dsl.Integer()
    original_file_type = dsl.Keyword()
    

class Index(dsl.AsyncDocument):
    document_id = dsl.Keyword()
    content = dsl.Text(analyzer="nori")
    vector = dsl.DenseVector(dims=1536)
    metadata = dsl.Object(IndexMetadata)
    tags = dsl.Keyword()
    is_deleted = dsl.Boolean()
    created_at = dsl.Date()
    updated_at = dsl.Date()



class Metadata(BaseModel):
    user_id: str = Field(
        ...,
        description="Unique identifier for the user who uploaded the document."
    )
    original_file_path: str = Field(
        ...,
        description="Original file path of the uploaded document."
    )
    original_file_name: str = Field(
        ...,
        description="Original file name of the uploaded document."
    )
    original_file_size: int = Field(
        ...,
        description="Original file size of the uploaded document."
    )
    original_file_type: str = Field(
        ...,
        description="Original file type of the uploaded document."
    )

    def to_es(self) -> IndexMetadata:
        return IndexMetadata(
            user_id=self.user_id, # type: ignore
            original_file_path=self.original_file_path, # type: ignore
            original_file_name=self.original_file_name, # type: ignore
            original_file_size=self.original_file_size, # type: ignore
            original_file_type=self.original_file_type # type: ignore
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
    vector: List[float] = Field(
        ...,
        description="The vector representation of the document, used for similarity search."
    )
    metadata: Metadata = Field(
        ...,
        description="Metadata associated with the document, such as user ID and file details."
    )
    tags: List[str] = Field(
        ...,
        description="Tags associated with the document for categorization or filtering."
    )
    is_deleted: bool = Field(
        default=False,
        description="Flag indicating whether the document is deleted. Default is False."
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

    def to_es(self) -> Index:
        return Index(
            document_id=self.document_id, # type: ignore
            content=self.content, # type: ignore
            vector=self.vector, # type: ignore
            metadata=self.metadata.to_es(), # type: ignore
            tags=self.tags, # type: ignore
            is_deleted=self.is_deleted, # type: ignore
            created_at=self.created_at, # type: ignore
            updated_at=self.updated_at # type: ignore
        ) 


DocumentT = TypeVar("DocumentT", bound="Document")

class AsyncCacheService: ...

class VectorStore(Generic[DocumentT]):

    __create_key = object()

    def __init__(
        self,
        key: object,
        vector_client: AsyncElasticsearch,
        embedding_service: AsyncOpenAI,
        cache_service: AsyncCacheService,
        indexname: str,
        document_class: type[DocumentT],
        *,
        vector_dimension: int = 1536
    ) -> None:
        
        if key != VectorStore.__create_key:
            raise ValueError("Use the create method to instantiate VectorStore.")
        
        self.vector_client = vector_client
        self.embedding_service = embedding_service
        self.cache_service = cache_service
        self.indexname = indexname
        self.vector_dimension = vector_dimension
        self.document_class = document_class        

    @classmethod
    async def create(
        cls,
        vector_client: AsyncElasticsearch,
        embedding_service: AsyncOpenAI,
        cache_service: AsyncCacheService,
        indexname: str,
        document_class: type[DocumentT],
        *,
        vector_dimension: int = 1536
    ) -> "VectorStore[DocumentT]":
        try:
            await document_class.get_es_definition().init(
                index=indexname,
                using=vector_client,
            )
        except Exception as indexErr:
            raise ValueError(
                f"Failed to initialize index {indexname}: {indexErr}"
            )
        
        return cls(
            key=cls.__create_key,
            vector_client=vector_client,
            embedding_service=embedding_service,
            cache_service=cache_service,
            indexname=indexname,
            document_class=document_class,
            vector_dimension=vector_dimension
        )

    
    async def add_documents(
        self,
        documents: List[DocumentT],
    ): 
        for doc in documents:
            doc.created_at = dt.datetime.now()
            doc.updated_at = dt.datetime.now()
            await doc.to_es().save(using=self.vector_client, index=self.indexname)
        
        return documents


    async def delete_by_ids(
        self,
        ids: List[str]
    ): ...

    async def search(
        self,
        query: str,
        top_k: int
    ) -> List[DocumentT]: ...


if __name__ == "__main__":
    # Example usage
    import asyncio
    import dotenv
    import os

    dotenv.load_dotenv()

    async def main():
        time= dt.datetime.now()
        vector_client = AsyncElasticsearch(
            hosts= os.getenv("ELASTICSEARCH_HOSTS", "http://localhost:9200"),
            api_key=os.getenv("ELASTICSEARCH_API_KEY", "")
        )
        init_endtime = dt.datetime.now()
        print(f"Vector client initialized in {init_endtime - time} seconds")
        embedding_service = AsyncOpenAI()
        cache_service = AsyncCacheService()
        indexname = "documents_index"
        
        async with vector_client as client:
            vector_store = await VectorStore.create(
                vector_client=client,
                embedding_service=embedding_service,
                cache_service=cache_service,
                indexname=indexname,
                document_class=Document
            )
            
            # Add a sample document
            doc = Document(
                document_id=str(uuid.uuid4()),
                content="Sample content",
                vector=[0.1] * 1536,  # Example vector
                metadata=Metadata(
                    user_id="user123",
                    original_file_path="/path/to/file",
                    original_file_name="file.txt",
                    original_file_size=1234,
                    original_file_type="text/plain"
                ),
                tags=["example", "test"]
            )
            
            await vector_store.add_documents([doc])
        

    asyncio.run(main())