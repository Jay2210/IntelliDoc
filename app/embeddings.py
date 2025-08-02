import os
import requests
from typing import List
from app.config import settings

JINA_API_KEY = settings.JINA_API_KEY
if not JINA_API_KEY:
    raise RuntimeError("Missing JINA_API_KEY environment variable")
JINA_URL     = "https://api.jina.ai/v1/embeddings"
JINA_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {JINA_API_KEY}"
}
JINA_MODEL = "jina-embeddings-v3"
JINA_TASK  = "retrieval.passage"

def embed_texts(texts: List[str]) -> List[List[float]]:
    payload = {
        "model": "jina-embeddings-v3",
        "task": "retrieval.passage",
        "input": texts,
    }
    resp = requests.post(JINA_URL, headers=JINA_HEADERS, json=payload, timeout=30)
    resp.raise_for_status()
    body = resp.json()

    if "data" in body and isinstance(body["data"], list):
        embeddings = []
        for item in body["data"]:
            if not isinstance(item, dict) or "embedding" not in item:
                raise RuntimeError(f"Unexpected item in Jina response: {item}")
            embeddings.append(item["embedding"])
        return embeddings

    if "embeddings" in body and isinstance(body["embeddings"], list):
        return body["embeddings"]

    raise RuntimeError(f"Unexpected Jina response format: {body}")
