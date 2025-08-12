import datetime as dt
import uuid
from typing import (
    List,
    Tuple, 
    TypeVar, 
    Generic,
    Any
)

import elasticsearch.dsl as dsl

from elasticsearch import AsyncElasticsearch
from openai import AsyncOpenAI
from pydantic import BaseModel, Field


class IndexFileMeta(dsl.InnerDoc):
    file_id = dsl.Keyword()
    file_path = dsl.Keyword()
    file_name = dsl.Keyword()
    file_size = dsl.Integer()
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
    prev: int = Field(
        default=-1,
        description="Previous page number, -1 if there is no previous page."
    )
    next: int = Field(
        default=-1,
        description="Next page number, -1 if there is no next page."
    )

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
    file_size: int = Field(
        ...,
        description="Original file size of the uploaded document."
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
            file_size=self.file_size, # type: ignore
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
        embedding_model: str = "text-embedding-3-small",
    ) -> None:
        
        if key != VectorStore.__create_key:
            raise ValueError("Use the create method to instantiate VectorStore.")
        
        self.vector_client = vector_client
        self.embedding_service = embedding_service
        self.cache_service = cache_service
        self.indexname = indexname
        self.embedding_model = embedding_model
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
        embedding_model: str = "text-embedding-3-small",
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
            embedding_model=embedding_model
        )

    async def delete_vectorstore(self) -> Exception | None:
        try:
            await self.vector_client.indices.delete(index=self.indexname)
        except Exception as e:
            return e
        
        return None
        
    async def add_documents(
        self,
        documents: List[DocumentT],
    ) -> Tuple[List[str], Exception | None]: 
        
        success_docs: List[str] = []

        for doc in documents:
            vector, err = await self._aembed({
                doc.document_id: doc.content
            })
            if err:
                continue
            
            doc.created_at = dt.datetime.now()
            doc.updated_at = dt.datetime.now()
            
            try:
                es_doc = doc.to_es(vector=vector[doc.document_id])
                await es_doc.save(using=self.vector_client, index=self.indexname)
            except Exception as e:
                continue

            success_docs.append(doc.document_id)
        
        return success_docs, None


    async def delete_by_ids(
        self,
        ids: List[str]
    ) -> Tuple[List[str], Exception | None]: 
        if not ids:
            return [], None

        query = {
            "query": {
                "terms": {
                    "document_id": ids
                }
            }
        }
        
        try:
            await self.vector_client.delete_by_query(
                index=self.indexname,
                body=query,
                conflicts="proceed"
            )
        except Exception as e:
            return [], e

        return ids, None


    async def search(
        self,
        query: str,
        filter: SearchFilter | None = None
    ) -> Tuple[List[DocumentT], Exception | None]:
        if not filter:
            filter = SearchFilter()
        
        vector_key = "query_vector"
        try:
            vector, err = await self._aembed({
                vector_key: query
            })
        except Exception as e:
            return [], e
        
        eff_at: dt.datetime = filter.effective_at
        filter_clauses = [
            dsl.Q("term", is_deleted=False),
            dsl.Q("range", **{"file_meta.effective_from": {"lte": eff_at}}),
            dsl.Q("range", **{"file_meta.effective_to": {"gte": eff_at}}),
        ]
        for tag in filter.tags:
            filter_clauses.append(dsl.Q("term", tags=tag))

        should_clauses = [
            dsl.Q("match", content={"query": query, "operator": "and"})
        ]
        bool_query = dsl.Q(
            "bool",
            filter=filter_clauses,
            should=should_clauses,
            minimum_should_match=1 if should_clauses else 0
        )
        oversample = filter.top_k * 3
        search_query = (
            dsl.AsyncSearch(
                using=self.vector_client,
                index=self.indexname
            )
            .query(bool_query)
            .knn(
                "vector",
                k=oversample,
                query_vector=vector[vector_key],
                num_candidates=max(oversample * 2, 100),
            )
            .extra(size=oversample)
        )
        try:
            resp = await search_query.execute()
        except Exception as e:
            return [], e

        results: List[DocumentT] = []
        if not resp.hits:
            return results, ValueError("No results found.")
        
        for hit in resp.hits:
            results.append(self.document_class.model_validate(hit))
        
        return results[:filter.top_k], None


    async def _aembed(
        self,
        texts: dict[str, str],
    ) -> Tuple[dict[str, List[float]], Exception | None]:
        
        embedding_results: dict[str, List[float]] = {}

        for key, text in texts.items():
            try:
                embeddings = (
                    await self.embedding_service.embeddings
                    .create(input=text, model=self.embedding_model)
                )
            except Exception as e:
                return {}, e

            embedding_results[key] = embeddings.data[0].embedding if embeddings.data else []

        return embedding_results, None

if __name__ == "__main__":
    # Example usage
    import asyncio
    import dotenv
    import os

    dotenv.load_dotenv()

    async def search():
        vector_client = AsyncElasticsearch(
            hosts=os.getenv("ELASTICSEARCH_HOSTS", "http://localhost:9200"),
            api_key=os.getenv("ELASTICSEARCH_API_KEY", "")
        )
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
            
            # Search for documents
            filter = SearchFilter(top_k=5, tags=["example"])
            results, err = await vector_store.search("Sample text for embedding", filter)
            if err:
                print(f"Error during search: {err}")
            else:
                for doc in results:
                    print(doc)

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
            docs = []
            for i in range(2):
                query = "Sample text for embedding, number: {}".format(i)
                doc = Document(
                    document_id=str(uuid.uuid4()),
                    content=query,
                    file_meta=FileMeta(
                        file_path="/path/to/file",
                        file_name="example.txt",
                        file_size=1234,
                        file_extension="txt",
                        file_type="text/plain",
                        file_description="An example text file",
                        effective_from=dt.datetime.now(),
                        effective_to=dt.datetime(9999, 12, 31),
                        author="John Doe",
                        department="Engineering"
                    ),
                    page_meta=PageMeta(
                        number=i,
                        total_pages=2,
                        prev=i - 1,
                        next= (i + 1 if i < 1 else -1)  # Next page only if not the last page
                    ),
                    tags=["example", "test"]
                )

                docs.append(doc)

            success, err = await vector_store.add_documents(docs)
            if err:
                print(f"Error adding documents: {err}")

    asyncio.run(search())