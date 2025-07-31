# app/retriever.py

from typing import List, Dict
from app.embeddings import embed_texts
from app.pinecone_client import index

def retrieve(
    query: str,
    top_k: int = 50,
    insurer: str = None
) -> List[Dict]:
    # 1) embed
    vectors = embed_texts([query])
    if not vectors:
        return []
    q_vec = [float(x) for x in vectors[0]]  # 768‐dim list

    # 2) build optional filter
    pinecone_filter = {}
    if insurer:
        pinecone_filter["insurer"] = {"$eq": insurer}

    # 3) query
    resp = index.query(
        vector=q_vec,
        top_k=top_k,
        include_metadata=True,
        filter=pinecone_filter or None,
    )
    print(f"Insurer: {insurer}, top_k: {top_k}, results: {len(resp.get('matches', []))}")
    # 4) normalize
    out = []
    for m in resp.get("matches", []):
        out.append({
            "id":     m["id"],
            "score":  m["score"],
            "source": m["metadata"].get("source"),
            "text":   m["metadata"].get("text"),
        })
    return out
