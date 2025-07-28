from pathlib import Path
from app.docs_loader import load_document

def test_loader_unsupported(tmp_path):
    p = tmp_path / "file.txt"
    p.write_text("hello")
    try:
        load_document(p)
    except ValueError as e:
        assert "Unsupported file type" in str(e)
    else:
        assert False, "Expected ValueError"
