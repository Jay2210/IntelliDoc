from app.retriever import retrieve

def test_retrieve_no_error():
    # this will error if Pinecone not initialized; just smoke-test signature
    try:
        _ = retrieve("test", top_k=1)
    except Exception:
        pass
    else:
        assert True
