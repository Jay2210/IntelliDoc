import sys
from pathlib import Path
from app.docs_loader import load_pdf  # the new PyMuPDF+pdfplumber loader

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_extraction.py <path/to/file.pdf>")
        sys.exit(1)

    pdf_path = Path(sys.argv[1])
    if not pdf_path.exists():
        print(f"File not found: {pdf_path}")
        sys.exit(1)

    md = load_pdf(pdf_path)
    out = pdf_path.with_suffix(".md")
    out.write_text(md, encoding="utf-8")
    print(f"🔍 Extraction written to {out}")

if __name__ == "__main__":
    main()
