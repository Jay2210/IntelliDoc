from pathlib import Path
import pdfplumber
from docx import Document
import mailparser

def load_pdf(path: Path) -> str:
    """
    Extracts text and tables from a PDF using pdfplumber.
    Tables are flattened into tab-separated rows.
    """
    pages = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            # extract page text
            text = page.extract_text()
            if text:
                pages.append(text)

            # extract tables
            for table in page.extract_tables():
                # each table is a list of rows, each row a list of cells
                # convert to TSV-like lines
                rows = ["\t".join(cell or "" for cell in row) for row in table]
                pages.append("\n".join(rows))

    # join pages with blank lines
    return "\n\n".join(pages)


def load_docx(path: Path) -> str:
    """
    Fallback for .docx: pull all paragraphs.
    """
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)


def load_eml(path: Path) -> str:
    """
    Fallback for .eml/.mime: prefer plain body, else text_plain.
    """
    m = mailparser.parse_from_file(str(path))
    if m.body:
        return m.body
    if m.text_plain:
        return "\n".join(m.text_plain)
    return ""


def load_document(path: Path) -> str:
    """
    Dispatch based on file suffix.
    """
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix in {".docx", ".doc"}:
        return load_docx(path)
    if suffix in {".eml", ".mime"}:
        return load_eml(path)
    raise ValueError(f"Unsupported file type: {suffix}")
