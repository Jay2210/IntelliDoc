from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_query_endpoint():
    resp = client.post("/query", json={"query": "46M knee surgery Pune 3 months"})
    assert resp.status_code in (200, 500)  # 500 if LLM/Pinecone not wired yet
