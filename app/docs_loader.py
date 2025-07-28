from pathlib import Path
from pdfminer.high_level import extract_text
from docx import Document
import mailparser

def load_pdf(path: Path) -> str:
    return extract_text(str(path))

def load_docx(path: Path) -> str:
    doc = Document(str(path))
    return "\n".join(p.text for p in doc.paragraphs)

def load_eml(path: Path) -> str:
    m = mailparser.parse_from_file(str(path))
    # prefer plain text body
    return m.body or "\n".join(m.text_plain) if m.text_plain else ""

def load_document(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return load_pdf(path)
    if suffix in {".docx", ".doc"}:
        return load_docx(path)
    if suffix in {".eml", ".mime"}:
        return load_eml(path)
    raise ValueError(f"Unsupported file type: {suffix}")
