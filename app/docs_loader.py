# app/docs_loader.py
from pathlib import Path
import fitz  # pip install pymupdf
import pdfplumber  # pip install pdfplumber
from docx import Document
import mailparser

def _table_to_markdown(table: list[list[str]]) -> str:
    """Convert a 2D list into a Markdown table string."""
    if not table:
        return ""
    # header + separator
    header = table[0]
    sep = ["---"] * len(header)
    lines = [
        "| " + " | ".join(row) + " |"
        for row in [header, sep] + table[1:]
    ]
    return "\n".join(lines)

def load_pdf(path: Path) -> str:
    """
    Extracts:
     - All text blocks via PyMuPDF (in reading order)
     - Then any tables on each page via pdfplumber, inserted right after the page's text.
    Returns a single string (with page breaks).
    """
    # Open both readers
    doc = fitz.open(str(path))
    pdf = pdfplumber.open(str(path))

    parts: list[str] = []

    for page_num, page in enumerate(doc):
        # 1) pull text blocks
        page_dict = page.get_text("dict")
        for block in page_dict["blocks"]:
            if block["type"] == 0:  # text block
                for line in block["lines"]:
                    parts.append("".join(span["text"] for span in line["spans"]))

        # 2) now pull tables via pdfplumber
        try:
            tb_page = pdf.pages[page_num]
            tables = tb_page.extract_tables()
            for tbl in tables:
                md = _table_to_markdown(tbl)
                if md.strip():
                    parts.append("")            # blank line before table
                    parts.append(md)
                    parts.append("")            # blank line after table
        except Exception:
            # if no tables or extraction fails, just skip
            pass

        parts.append("")  # page break

    pdf.close()
    doc.close()
    return "\n".join(parts)

def load_docx(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)

def load_eml(path: Path) -> str:
    m = mailparser.parse_from_file(str(path))
    if m.body:
        return m.body
    if m.text_plain:
        return "\n".join(m.text_plain)
    return ""

def load_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix in {".doc", ".docx"}:
        return load_docx(path)
    if suffix in {".eml", ".mime"}:
        return load_eml(path)
    raise ValueError(f"Unsupported file type: {suffix}")
