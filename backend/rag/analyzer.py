import uuid
import datetime as dt
from typing import List, Tuple, Callable
from pydantic import BaseModel, Field

from sqlalchemy import select
from sqlalchemy.orm import Session

import backend.db.file_tables as tbl
import backend.models as mdl
import backend.rag.models as rag
import backend._types as t
import backend.utils.logger as lg

from agents.main import AsyncSimpleAgent

class FileAnalyzed(BaseModel):
    type: str = Field(
        ...,
        description="문서의 타입입니다. 예: 송장, 계약서, 보고서 등",
        examples=['송장', '계약서', '보고서']
    )
    description: str = Field(
        ...,
        description="문서의 간단한 설명입니다.",
        examples=['2025년도 최고급 AI 해외인재 유치지원 사업 재공고']
    )
    effective_from: dt.datetime = Field(
        default=dt.datetime.now(),
        description="문서의 유효 시작일입니다. 기본값은 현재 시간입니다.",
        examples=[dt.datetime.now()]
    )
    effective_to: dt.datetime = Field(
        ...,
        description="문서의 유효 종료일입니다.",
        examples=[dt.datetime(9999, 12, 31)]
    )
    author: str = Field(
        default="unknown",
        description="문서의 저자입니다.",
        examples=['홍길동', '이순신'],
    )
    department: t.DepartmentsLiteral = Field(
        default="Common",
        description="문서가 속한 부서명입니다. 기본값은 Common입니다.",
        examples=['Common', 'HR'],
    )

    @staticmethod
    def system_prompt() -> str:
        return """
## 역할
당신은 문서 분석기입니다.
당신의 역할은 주어진 문서를 분석하고, 그 내용을 이해하며, 필요한 정보를 추출하는 것입니다.

## 요구사항
- 문서의 저자를 식별가능해야 합니다. 식별 불가능할 시 'unknown'으로 표기하시오.
- 문서의 타입을 식별 가능해야 합니다. (송장, 계약서, 보고서 등)
- 문서의 유효기간을 식별가능해야 합니다. 기본값은 현재 날짜부터 9999년 12월 31일까지입니다.
- 문서의 부서명을 식별 가능해야합니다. 기본값은 Common입니다.

## 현재 시간
{time}
""".format(time=dt.datetime.now().isoformat())


class Tags(BaseModel):
    tags: List[str] = Field(
        ...,
        description="문서에 적용할 태그 목록입니다.",
        examples=[['AI', '보고서'], ['계약서', '법률']]
    )

    @staticmethod
    def system_prompt() -> str:
        return """
## 역할
당신은 문서 분석기입니다.
당신의 역할은 주어진 문서를 분석하고, 그 내용을 이해해서, 필요한 정보를 추출하는 것입니다.

## 요구사항
- 문서에 적용할 태그 목록을 식별 가능해야 합니다.

"""


async def analyze(
    contents_by_page: List[str],
    *,
    ai: AsyncSimpleAgent,
    file: mdl.File,
    split_func: Callable,
) -> Tuple[List[rag.Document], Exception | None]:
    """
    Analyze the contents of a file and extract relevant information.
    split func must returns `List[str]`

    Args:
        contents_by_page (List[str]): The contents of the file split by page.
        ai (AsyncSimpleAgent): The AI agent to use for analysis.
        file (mdl.File): The file metadata.
        split_func (Callable): The function to split the content into chunks.

    Returns:
        Tuple[List[rag.Document], Exception | None]: The analyzed documents and any error that occurred.

    """
    lg.logger.info(f"Analyzing Starts with file {file.file_id} for user {file.author_id}!!")

    fileanalyzed, err = await ai.aparse(
        messages=[
            {'role': 'system', 'content': FileAnalyzed.system_prompt()},
            {'role': 'user', 'content': contents_by_page[0]}
        ],
        response_fmt=FileAnalyzed,
        deployment_id="gpt-5-nano"
    )
    if err or not fileanalyzed:
        return [], err
    
    filemeta = rag.FileMeta(
        file_id=file.file_id,
        file_path=file.file_path,
        file_name=file.file_name,
        file_extension=file.file_extension,
        file_type=fileanalyzed.type,
        file_description=fileanalyzed.description,
        effective_from=fileanalyzed.effective_from,
        effective_to=fileanalyzed.effective_to,
        author=fileanalyzed.author,
        department=fileanalyzed.department
    )

    documents: List[rag.Document] = []
    for page_idx, content in enumerate(contents_by_page):
        lg.logger.info(f"Processing page {page_idx + 1} of {len(contents_by_page)}")

        pagemeta = rag.PageMeta(
            number = page_idx + 1,
            total_pages=len(contents_by_page),
        )
        chunks: List[str] = split_func(content)

        for chunk_idx, chunk in enumerate(chunks):
            lg.logger.info(f"Processing chunk {chunk_idx + 1} of {len(chunks)} in page {page_idx + 1}")

            document_id = "doc-" + str(uuid.uuid4())
            tags, err = await ai.aparse(
                messages=[
                    {'role': 'system', 'content': Tags.system_prompt()},
                    {'role': 'user', 'content': content}
                ],
                response_fmt=Tags,
                deployment_id="gpt-5-nano"
            )
            if err or not tags:
                lg.logger.error(f"Error parsing tags for chunk {chunk_idx + 1} in page {page_idx + 1}: {err}")
                continue
        
            document = rag.Document(
                document_id=document_id,
                content=chunk,
                tags=tags.tags,
                file_meta=filemeta,
                page_meta=pagemeta
            )

            documents.append(document)
            lg.logger.info(f"Document {document_id} created with {len(chunk)} characters.")

    return documents, None