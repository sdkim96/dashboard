from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Generator, List, Tuple

import azure.ai.documentintelligence.models as mdl
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient


from backend.config import CONFIG


@asynccontextmanager
async def get_ocr(
    *,
    endpoint: str | None = None, 
    key: str | None = None
) -> AsyncGenerator[DocumentIntelligenceClient, None]:
    
    client = DocumentIntelligenceClient(
        endpoint=endpoint or CONFIG.OCR_ENDPOINT,
        credential=AzureKeyCredential(key=key or CONFIG.OCR_API_KEY)
    )
    try:
        yield client
    finally:
        await client.close()

async def read(
    blob_url: str
) -> Tuple[mdl.AnalyzeResult | None, Exception | None]:
    
    try:
        async with get_ocr() as client:
            poller = await client.begin_analyze_document(
                "prebuilt-read", 
                mdl.AnalyzeDocumentRequest(url_source=blob_url)
            )
            result = await poller.result()
    except Exception as e:
        return None, e
    
    return result, None

async def analyze_pages(target: List[mdl.DocumentPage]): 
    page: mdl.DocumentPage
    for page in target:
        for line in page.lines:
            print(f"Line: {line.content} (Bounding Box: {line.polygon})")

async def analyze_paragraphs(target: List[mdl.DocumentParagraph]):
    paragraph: mdl.DocumentParagraph
    for paragraph in target:
        print(f"Paragraph: {paragraph.content}")
        
async def analyze_styles(target: List[mdl.DocumentStyle] | None): ...
