import os
from typing import List, Tuple, Any, cast

from elasticsearch import AsyncElasticsearch
from openai import AsyncOpenAI

import backend.models as mdl
import backend.rag as rag
import backend.config as cfg

async def rag_tool(
    query: str,
    tags: str
) -> str: 
    """
    ## RAG Tool
    이 도구는 주어진 쿼리와 태그를 사용하여 RAG(정보 검색 및 생성) 시스템에서 문서를 검색합니다.
    반드시 쿼리는 간결하고 명확해야 하며, 유저의 지난 질문들에서 핵심 정보들로만 추출해야 합니다.
    검색할 때 필요하지 않은 키워드들은 과감히 제거하세요. 예를들어 `내부`, `문서`와 같은 단어들은 제거해야 합니다.

    ## 좋은 예시
    - `내부 문서에서 사이냅소프트에 관한 정보를 찾아줘` -> `사이냅소프트에 관한 정보`

    """
    
    vector_client = AsyncElasticsearch(
        hosts=cfg.CONFIG.ELASTICSEARCH_HOSTS,
        api_key=cfg.CONFIG.ELASTICSEARCH_API_KEY
    )
    embedding_service = AsyncOpenAI()
    cache_service = rag.AsyncCacheService()
    indexname = "document"
    
    async with vector_client as client:
        vector_store = await rag.VectorStore.create(
            vector_client=client,
            embedding_service=embedding_service,
            cache_service=cache_service,
            indexname=indexname,
            document_class=rag.Document
        )
        
        # Search for documents
        filter = rag.SearchFilter(top_k=5, tags=[tags])
        results, err = cast(
            Tuple[List[rag.Document], Exception | None],
            await vector_store.search(
                query,
                filter
            )
        )
        if err:
            return ""
    
    rag_description = ""
    for r in results:
        rag_description += r.to_desription()

    return rag_description


TOOL_MAP = {
    'tool-123e4567-e89b-12d3-a456-426614174000': rag_tool
}


async def choose_tools(tools: List[mdl.Tool]) -> List[dict[str, Any]]:
    tool_specs = []
    for tool in tools:
        if tool.tool_id in TOOL_MAP:
            spec = {}
            spec['name'] = TOOL_MAP[tool.tool_id].__name__
            spec['description'] = TOOL_MAP[tool.tool_id].__doc__
            spec['fn'] = TOOL_MAP[tool.tool_id]
            tool_specs.append(spec)

    return tool_specs
