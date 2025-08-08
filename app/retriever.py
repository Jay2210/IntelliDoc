# app/retriever.py

from typing import List, Dict
from app.embeddings import embed_texts
from app.pinecone_client import index

def retrieve(
    query: str,
    top_k: int = 50,
    insurer: str = None
) -> List[Dict]:
    vectors = embed_texts([query], task="retrieval.passage")
    if not vectors:
        return []
    q_vec = [float(x) for x in vectors[0]]

    pinecone_filter = {}
    if insurer:
        pinecone_filter["insurer"] = {"$eq": insurer}

    resp = index.query(
        vector=q_vec,
        top_k=top_k,
        include_metadata=True,
        filter=pinecone_filter or None,
    )
    print(f"Insurer: {insurer}, top_k: {top_k}, results: {len(resp.get('matches', []))}")
    out = []
    for m in resp.get("matches", []):
        out.append({
            "id":     m["id"],
            "score":  m["score"],
            "source": m["metadata"].get("source"),
            "text":   m["metadata"].get("text"),
        })
    return out
