from app.chunking import chunk_text

def test_chunk_small():
    text = "a " * 100
    chunks = chunk_text(text)
    assert isinstance(chunks, list)
    assert "".join(chunks).startswith("a")
