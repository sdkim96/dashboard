import datetime as dt
import uuid
from typing import (
    List,
    Tuple, 
    Generic,
)

import elasticsearch.dsl as dsl

from elasticsearch import AsyncElasticsearch
from openai import AsyncOpenAI

import backend.rag.models as mdl



class AsyncCacheService: ...

class VectorStore(Generic[mdl.DocumentT]):

    __create_key = object()

    def __init__(
        self,
        key: object,
        vector_client: AsyncElasticsearch,
        embedding_service: AsyncOpenAI,
        cache_service: AsyncCacheService,
        indexname: str,
        document_class: type[mdl.DocumentT],
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
        document_class: type[mdl.DocumentT],
        *,
        embedding_model: str = "text-embedding-3-small",
    ) -> "VectorStore[mdl.DocumentT]":
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
        documents: List[mdl.DocumentT],
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
        filter: mdl.SearchFilter | None = None
    ) -> Tuple[List[mdl.DocumentT], Exception | None]:
        if not filter:
            filter = mdl.SearchFilter()
        
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

        results: List[mdl.DocumentT] = []
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
                document_class=mdl.Document
            )
            
            # Search for documents
            filter = mdl.SearchFilter(top_k=5, tags=["example"])
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
                document_class=mdl.Document
            )
            
            # Add a sample document
            docs = []
            for i in range(2):
                query = "Sample text for embedding, number: {}".format(i)
                doc = mdl.Document(
                    document_id=str(uuid.uuid4()),
                    content=query,
                    file_meta=mdl.FileMeta(
                        file_path="/path/to/file",
                        file_name="example.txt",
                        file_extension="txt",
                        file_type="text/plain",
                        file_description="An example text file",
                        effective_from=dt.datetime.now(),
                        effective_to=dt.datetime(9999, 12, 31),
                        author="John Doe",
                        department="Engineering"
                    ),
                    page_meta=mdl.PageMeta(
                        number=i,
                        total_pages=2,
                    ),
                    tags=["example", "test"]
                )

                docs.append(doc)

            success, err = await vector_store.add_documents(docs)
            if err:
                print(f"Error adding documents: {err}")

    asyncio.run(main())