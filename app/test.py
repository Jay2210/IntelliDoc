# test_loader.py
import argparse
from pathlib import Path
import sys

# Import the function from your other file
from docs_loader import load_document

def main():
    """
    Main function to parse command-line arguments and process the document.
    """
    parser = argparse.ArgumentParser(
        description="Test the document loader by extracting text from a given file."
    )
    parser.add_argument(
        "file_path", 
        type=Path, 
        help="Path to the document file (PDF, DOCX, etc.) to process."
    )

    args = parser.parse_args()
    doc_path = args.file_path

    if not doc_path.is_file():
        print(f"Error: The file was not found at '{doc_path}'")
        sys.exit(1)

    print(f"Processing document: {doc_path.name}...")

    try:
        content = load_document(doc_path)
        print("\n" + "="*25 + " EXTRACTED CONTENT " + "="*25 + "\n")
        print(content)
        print("\n" + "="*27 + " END OF CONTENT " + "="*27 + "\n")
        Path.write_bytes(doc_path.with_suffix('.md'), content.encode('utf-8'))
    except Exception as e:
        print(f"\nAn error occurred during processing: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()