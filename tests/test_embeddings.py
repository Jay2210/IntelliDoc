from app.embeddings import embed_texts

def test_embed_length():
    vecs = embed_texts(["hello", "world"])
    assert len(vecs) == 2
    assert len(vecs[0]) == 1536
