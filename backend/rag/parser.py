import json
from contextlib import asynccontextmanager

from typing import Any, AsyncGenerator, List, Tuple
from pydantic.dataclasses import dataclass

import azure.ai.documentintelligence.models as mdl

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient

from backend.config import CONFIG


@dataclass
class AnalyzedParagraph:
    content: str
    page: int
    polygon: List[float]

@dataclass
class AnalyzedTable:
    content: str
    page: int
    idx_to_remove: List[int]

@dataclass
class FigureElement:
    content: str
    polygon: List[float]

@dataclass
class AnalyzedFigure:
    elements: List[FigureElement]
    figure_polygon: List[float]
    figure_caption: str
    page: int
    idx_to_remove: List[int]

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
    blob_url: str,
    mock_path: str | None = None
) -> Tuple[mdl.AnalyzeResult | None, Exception | None]:
    """ Reads a document from Azure Blob Storage and returns the analysis result.

    Args:
        blob_url (str): The URL of the document to analyze.
        mock_path (str | None): Optional path to a mock JSON file for testing purposes.
    
    Returns:
        Tuple[mdl.AnalyzeResult | None, Exception | None]: A tuple containing the analysis
    
    """
    if mock_path:
        with open(mock_path, "r") as f:
            mock_data = json.load(f)
        
        data = mock_data.get('analyzeResult', {})
        data = _convert_keys_into_snake_case(data)
        return mdl.AnalyzeResult(**data), None # type: ignore

    try:
        async with get_ocr() as client:
            poller = await client.begin_analyze_document(
                "prebuilt-layout", 
                mdl.AnalyzeDocumentRequest(url_source=blob_url)
            )
            result = await poller.result()
    except Exception as e:
        return None, e
    
    return result, None
    

async def analyze_paragraphs(
    unanalyzed: List[mdl.DocumentParagraph] | None
) -> List[AnalyzedParagraph]:
    """ Anaylzes Azure's paragraphs from the document 
    and returns a list of AnalyzedParagraph.

    Args:
        unanalyzed (List[mdl.DocumentParagraph] | None): List of paragraphs to analyze.
    Returns:
        out(List[AnalyzedParagraph]): A list of AnalyzedParagraph objects containing the content and page number.
    """
    paragraphs: List[AnalyzedParagraph] = []
    if not unanalyzed:
        return paragraphs
    
    role_prefix: dict[mdl.ParagraphRole, str] = {
        mdl.ParagraphRole.PAGE_HEADER: "<header> ",
        mdl.ParagraphRole.PAGE_FOOTER: "<footer> ",
        mdl.ParagraphRole.PAGE_NUMBER: "<",
        mdl.ParagraphRole.TITLE: "## ",
        mdl.ParagraphRole.SECTION_HEADING: "### ",
        mdl.ParagraphRole.FOOTNOTE: "",
        mdl.ParagraphRole.FORMULA_BLOCK: "<formula_block>"
    }
    role_suffix: dict[mdl.ParagraphRole, str] = {
        mdl.ParagraphRole.PAGE_HEADER: "</header>\n",
        mdl.ParagraphRole.PAGE_FOOTER: "</footer>\n",
        mdl.ParagraphRole.PAGE_NUMBER: ">\n",
        mdl.ParagraphRole.TITLE: "\n",
        mdl.ParagraphRole.SECTION_HEADING: "\n",
        mdl.ParagraphRole.FOOTNOTE: "</footnote>\n",
        mdl.ParagraphRole.FORMULA_BLOCK: "</formula_block>"
    }

    pagenum = 1
    for p in unanalyzed:
        polygon = []
        if p._data['bounding_regions']:
            pagenum = p._data['bounding_regions'][0]['page_number']
            polygon = p._data['bounding_regions'][0]['polygon']

        content = p.content
        if p.role and isinstance(p.role, mdl.ParagraphRole):
            prefix = role_prefix.get(p.role, "")
            suffix = role_suffix.get(p.role, "")
            content = f"{prefix}{p.content}{suffix}"

        paragraphs.append(AnalyzedParagraph(content=content, page=pagenum, polygon=polygon))

    return paragraphs


async def analyze_tables(
    unanalyzed: List[mdl.DocumentTable] | None, 
) -> List[AnalyzedTable]: 
    """ Analyzes tables from the document and returns a markdown representation and index number of paragraphs to remove.
    Args:
        unanalyzed (List[mdl.DocumentTable] | None): List of tables to analyze.

    Returns:
        List[AnalyzedTable]: A list containing the analyzed tables.
    """
    
    tables: List[AnalyzedTable] = []

    if not unanalyzed:
        return tables

    for t in unanalyzed:
        idx_to_rm: List[int] = []
        table_analyzed: List[List[str]] = []
        page = t._data['bounding_regions'][0]['page_number'] if t._data['bounding_regions'] else 1
        for _ in range(t._data['row_count']):
            table_analyzed.append([""] * (t._data['column_count']))

        for cell in t.cells:
            rowidx = cell._data['row_index']
            colidx = cell._data['column_index']
            table_analyzed[rowidx][colidx] = cell.content

            if cell.elements:
                para_idxs = cell.elements
                for idx in para_idxs:
                    target = idx.split("/")[-1]
                    if target.isdigit():
                        idx_to_rm.append(int(target))

        markdown_document = ""
        for rowidx, rowcontent in enumerate(table_analyzed):
            markdown = "| " + " | ".join(rowcontent) + " |"
            if rowidx == 0:
                markdown += "\n" + "| " + " | ".join(["---"] * len(rowcontent)) + " |"
            markdown_document += markdown + "\n"

        caption = t.caption
        if caption:
            markdown_document += f"*{caption.content}*\n"
            eles_to_rm = caption.elements
            if eles_to_rm:
                for idx in eles_to_rm:
                    target = idx.split("/")[-1]
                    if target.isdigit():
                        idx_to_rm.append(int(target))
        
        tables.append(
            AnalyzedTable(content=markdown_document, idx_to_remove=idx_to_rm, page=page)
        )

    return tables

async def analyze_figures(
    unanalyzed: List[mdl.DocumentFigure] | None,
    reference_paragrahs: List[AnalyzedParagraph]
) -> List[AnalyzedFigure]: 
    """Analyzes figures from the document and returns a list of AnalyzedFigure.
    
    Args:
        unanalyzed (List[mdl.DocumentFigure] | None): List of figures to analyze.
        reference_paragrahs (List[AnalyzedParagraph]): List of paragraphs to reference for figure analysis.
    
    Returns:
        List[AnalyzedFigure]: A list containing the analyzed figures.
    """
    figures: List[AnalyzedFigure] = []

    if not unanalyzed:
        return figures

    for f in unanalyzed:
        idx_to_rm: List[int] = []
        elements: List[FigureElement] = []
        figure_polygon = f._data['bounding_regions'][0]['polygon'] if f._data['bounding_regions'] else []
        figure_caption = ""

        if f.elements:
            for idx in f.elements:
                target = idx.split("/")[-1]
                if target.isdigit():
                    content_idx = int(target)
                    parafound = reference_paragrahs[content_idx]
                    
                    elements.append(FigureElement(
                        content=parafound.content,
                        polygon=parafound.polygon,
                    ))
                    idx_to_rm.append(int(target))
        
        if f.caption:
            figure_caption = f.caption.content
            if f.caption.bounding_regions:
                figure_polygon = f.caption.bounding_regions[0].polygon
            if f.caption.elements:
                for idx in f.caption.elements:
                    target = idx.split("/")[-1]
                    if target.isdigit():
                        idx_to_rm.append(int(target))
            
        figure = AnalyzedFigure(
            elements=elements,
            figure_polygon=figure_polygon,
            idx_to_remove=idx_to_rm,
            figure_caption=figure_caption,
            page=f._data['bounding_regions'][0]['page_number'] if f._data['bounding_regions'] else 1
        )
        figures.append(figure)

    return figures


async def main():
    blob_url = "https://example.com/path/to/your/document.pdf"
    mock_path = 'many.json'  # Set to a path for mock data if needed

    result, error = await read(blob_url, mock_path)
    if error or not result:
        print(f"Error reading document: {error}")
        return
    
    paras = await analyze_paragraphs(result.paragraphs)
    tables= await analyze_tables(result.tables)
    figures = await analyze_figures(result.figures, paras)

    new_paras = paras[:]
    new_paras = paras[:]  # 원본 복사

    remove_idxs = set()
    for tbl in tables:
        remove_idxs.update(tbl.idx_to_remove)
    for fig in figures:
        remove_idxs.update(fig.idx_to_remove)

    for idx in sorted(remove_idxs, reverse=True):
        if 0 <= idx < len(new_paras):
            del new_paras[idx]

    for tbl in tables:
        if tbl.idx_to_remove:
            insert_idx = tbl.idx_to_remove[0]
            new_paras.insert(
                insert_idx,
                AnalyzedParagraph(
                    content=tbl.content,
                    page=tbl.page,
                    polygon=[]
                )
            )

    for fig in figures:
        if fig.idx_to_remove:
            insert_idx = fig.idx_to_remove[0]
            figure_text = "\n".join([f"{e.content}, Polygon: {e.polygon}" for e in fig.elements])
            if fig.figure_caption:
                figure_text += f"\n*{fig.figure_caption}*"
            new_paras.insert(
                insert_idx,
                AnalyzedParagraph(
                    content=figure_text,
                    page=fig.page,
                    polygon=fig.figure_polygon
                )
            )
    for para in new_paras:
        print(f"{para.content}, Polygon: {para.polygon}")
        
        

def _convert_to_snakecase(value: str) -> str:
    """
    Converts a string to snake_case.
    
    Args:
        value (str): The string to convert.
    
    Returns:
        str: The converted string in snake_case.
    """
    return ''.join(['_' + i.lower() if i.isupper() else i for i in value]).lstrip('_')

def _convert_keys_into_snake_case(data):
    if isinstance(data, dict):
        return {_convert_to_snakecase(key): _convert_keys_into_snake_case(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_convert_keys_into_snake_case(item) for item in data]
    return data

if __name__ == "__main__":
    # Example usage
    import asyncio
    asyncio.run(main())
