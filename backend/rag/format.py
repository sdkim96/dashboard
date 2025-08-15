import json
from contextlib import asynccontextmanager

from typing import (
    Any, 
    AsyncGenerator, 
    List, 
    Tuple
)

import azure.ai.documentintelligence.models as mdl
import numpy as np

from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence.aio import DocumentIntelligenceClient
from pydantic.dataclasses import dataclass

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
class AnalyzedFigure:
    content: str
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


async def format_file(
    blob_url: str, 
    mock_path: str | None = None
) -> Tuple[List[str], Exception | None]:
    """ Main pipeline to read a document, format paragraphs, tables, and figures, and return the result as markdown.
    Args:
        blob_url (str): The URL of the document to analyze.
        mock_path (str | None): Optional path to a mock JSON file for testing purposes.
    
    Returns:
        Tuple[List[str], Exception | None]: A tuple containing the markdown result per page and any exception that occurred
    """
    unanalyzed, error = await read(blob_url, mock_path)
    if error or not unanalyzed:
        print(f"Error reading document: {error}")
        return [], error

    paras = await analyze_paragraphs(unanalyzed.paragraphs)
    tables = await analyze_tables(unanalyzed.tables, reference_paragrahs=paras)
    figures = await analyze_figures(unanalyzed.figures, reference_paragrahs=paras)

    new_paras = {}
    for i, para in enumerate(paras):
        new_paras[i] = para

    remove_idxs = set()
    for tbl in tables:
        remove_idxs.update(tbl.idx_to_remove)
    for fig in figures:
        remove_idxs.update(fig.idx_to_remove)

    for idx in sorted(remove_idxs, reverse=True):
        if idx in new_paras:
            del new_paras[idx]

    for tbl in tables:
        if tbl.idx_to_remove:
            insert_idx = tbl.idx_to_remove[0]
            new_paras[insert_idx] = AnalyzedParagraph(
                content=tbl.content,
                page=tbl.page,
                polygon=[]
            )

    for fig in figures:
        if fig.idx_to_remove:
            insert_idx = fig.idx_to_remove[0]
            new_paras[insert_idx] = AnalyzedParagraph(
                content=fig.content,
                page=fig.page,
                polygon=[]
            )
    
    sorted_items = sorted(new_paras.items(), key=lambda x: x[0])
    result_markdown: dict[int, str] = {}
    for idx, para in sorted_items:
        current_page = result_markdown.get(para.page, "")
        current_page += para.content + "\n\n"
        result_markdown[para.page] = current_page

    markdown_per_page = [content for _, content in result_markdown.items()]

    return markdown_per_page, None



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
        mdl.ParagraphRole.PAGE_HEADER: "> ",
        mdl.ParagraphRole.PAGE_FOOTER: "> ",
        mdl.ParagraphRole.PAGE_NUMBER: "*Page ",
        mdl.ParagraphRole.TITLE: "## ",
        mdl.ParagraphRole.SECTION_HEADING: "### ",
        mdl.ParagraphRole.FOOTNOTE: "<footnote> ",
        mdl.ParagraphRole.FORMULA_BLOCK: "<formula_block>"
    }
    role_suffix: dict[mdl.ParagraphRole, str] = {
        mdl.ParagraphRole.PAGE_HEADER: "\n",
        mdl.ParagraphRole.PAGE_FOOTER: "\n",
        mdl.ParagraphRole.PAGE_NUMBER: "*\n",
        mdl.ParagraphRole.TITLE: "\n",
        mdl.ParagraphRole.SECTION_HEADING: "\n",
        mdl.ParagraphRole.FOOTNOTE: "</footnote>\n",
        mdl.ParagraphRole.FORMULA_BLOCK: "</formula_block>\n"
    }
    replace_map = {
        ":selected:": "☑",
        ":unselected:": "☐",
    }

    pagenum = 1
    for p in unanalyzed:
        polygon = []
        if p.bounding_regions:
            pagenum = p.bounding_regions[0].page_number
            polygon = p.bounding_regions[0].polygon

        content = p.content
        for old, new in replace_map.items():
            content = content.replace(old, new)
        if p.role and isinstance(p.role, mdl.ParagraphRole):
            prefix = role_prefix.get(p.role, "")
            suffix = role_suffix.get(p.role, "")
            content = f"{prefix}{p.content}{suffix}"

        paragraphs.append(AnalyzedParagraph(content=content, page=pagenum, polygon=polygon))

    return paragraphs


async def analyze_tables(
    unanalyzed: List[mdl.DocumentTable] | None,
    reference_paragrahs: List[AnalyzedParagraph],
) -> List[AnalyzedTable]: 
    """ Analyzes tables from the document and returns a markdown representation and index number of paragraphs to remove.
    Args:
        unanalyzed (List[mdl.DocumentTable] | None): List of tables to analyze.
        reference_paragrahs (List[AnalyzedParagraph]): List of paragraphs to reference for table analysis.

    Returns:
        List[AnalyzedTable]: A list containing the analyzed tables.
    """
    
    tables: List[AnalyzedTable] = []

    if not unanalyzed:
        return tables

    for t in unanalyzed:
        idx_to_rm: List[int] = []
        table_analyzed: List[List[str]] = []
        page = t.bounding_regions[0].page_number if t.bounding_regions else 1
        for _ in range(t.row_count):
            table_analyzed.append([""] * (t.column_count))

        for cell in t.cells:
            rowidx = cell.row_index
            colidx = cell.column_index
            
            cell_content = cell.content
            if cell.elements:
                reference = cell.elements[0].split("/")[-1]
                if reference.isdigit():
                    cell_content = reference_paragrahs[int(reference)].content

            table_analyzed[rowidx][colidx] = cell_content

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
    reference_paragrahs: List[AnalyzedParagraph],
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
        figure_caption = ""
        figure_elements: List[AnalyzedParagraph] = []

        if f.elements:
            for idx in f.elements:
                target = idx.split("/")[-1]
                if target.isdigit():
                    content_idx = int(target)
                    parafound = reference_paragrahs[content_idx]
                    figure_elements.append(parafound)
                    idx_to_rm.append(int(target))
        
        if f.caption:
            figure_caption = f.caption.content
            if f.caption.elements:
                for idx in f.caption.elements:
                    target = idx.split("/")[-1]
                    if target.isdigit():
                        idx_to_rm.append(int(target))

        rendered = _ascii_render(
            elements=figure_elements, 
            width=60, 
            height=20,
            caption=figure_caption,
        )

        figures.append(
            AnalyzedFigure(
                content=rendered,
                page=f.bounding_regions[0].page_number if f.bounding_regions else 1,
                idx_to_remove=idx_to_rm,
            )
        )
    return figures

        
def _ascii_render(
    elements: List[AnalyzedParagraph], 
    width=60, 
    height=20,
    caption: str | None = None
) -> str:
    """ Renders a list of AnalyzedParagraph elements into ASCII art.

    Args:
        elements (List[AnalyzedParagraph]): List of AnalyzedParagraph elements to render.
        width (int): Width of the ASCII art canvas.
        height (int): Height of the ASCII art canvas.
        caption (str | None): Optional caption to append at the end of the ASCII art.
    
    Returns:
        str: The rendered ASCII art as a string.
    
    """

    all_x = []
    all_y = []

    for elem in elements:
        all_x.extend(elem.polygon[0::2])
        all_y.extend(elem.polygon[1::2])
    
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    canvas = [[' ' for _ in range(width)] for _ in range(height)]
    
    for elem in elements:

        x = np.mean(elem.polygon[0::2])
        y = np.mean(elem.polygon[1::2])
        
        cx = int((x - min_x) / (max_x - min_x) * (width - 1))
        cy = int((y - min_y) / (max_y - min_y) * (height - 1))
        
        text = elem.content
        for i, char in enumerate(text):
            if 0 <= cx + i < width and 0 <= cy < height:
                canvas[cy][cx + i] = char
    
    ascii_art = '\n'.join([''.join(row) for row in canvas]) 
    if caption:
        ascii_art += f"\n\n*{caption}*"
    return ascii_art


def _convert_to_snakecase(value: str) -> str:
    """
    Converts a string to snake_case.
    
    Args:
        value (str): The string to convert.
    
    Returns:
        str: The converted string in snake_case.
    """
    return ''.join(['_' + i.lower() if i.isupper() else i for i in value]).lstrip('_')

def _convert_keys_into_snake_case(data: Any) -> Any:
    """ Recursively converts keys in a dictionary or list to snake_case.
    
    Args:
        data (Any): The data structure to convert.

    Returns:
        Any: The converted data structure with keys in snake_case.
    """

    if isinstance(data, dict):
        return {_convert_to_snakecase(key): _convert_keys_into_snake_case(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [_convert_keys_into_snake_case(item) for item in data]
    return data



