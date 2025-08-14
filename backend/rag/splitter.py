from typing import List, Tuple

def split_by_header(
    text: str,
    delimeter: List[str] = ['##', '###'],
    ignore_first_seen_header: bool = True
) -> List[str]:
    """
    Splits the text into sections based on the specified headers.
    
    Args:
        text (str): The text to be split.
        delimeter (List[str]): List of header prefixes to split by.
        ignore_first_seen_header (bool): If True, the first occurrence of a header will not start a new section.

    Returns:
        List[str]: A list of sections split by the specified headers.
    """
    sections = []
    current_section = ""
    seen = False
    
    lines = text.splitlines()
    for line in lines:
        if any(
            line.startswith(header) 
            for header in delimeter
        ):
            if ignore_first_seen_header and not seen:
                seen = True
                current_section += line + "\n"
                continue
            
            sections.append(current_section.strip())
            current_section = ""
            continue

        current_section += line + "\n"
    
    if len(sections) == 0 and current_section.strip():
        sections.append(current_section.strip())
    
    return sections
        