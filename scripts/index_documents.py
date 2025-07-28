import os
from pathlib import Path

from app.docs_loader import load_document
from app.chunking import chunk_text
from app.embeddings import embed_texts
from app.pinecone_client import get_index
from app.utils import get_logger

logger = get_logger(__name__)

def run() -> int:
    docs_dir = Path(os.getenv("DOCS_PATH", "data/docs"))
    idx = get_index()
    total = 0

    for path in docs_dir.iterdir():
        if not path.is_file(): continue
        text = load_document(path)
        chunks = chunk_text(text)
        vectors = embed_texts(chunks)
        batch = []
        for i, (vec, chunk) in enumerate(zip(vectors, chunks)):
            vid = f"{path.stem}-{i}"
            batch.append((vid, vec, {"source": path.name, "text": chunk}))
            
        batch =[]
        for i, (vec, chunk) in enumerate(zip(vectors, chunks)):
            vid = f"{path.stem}-{i}"
            batch.append((vid, vec, {"source": path.name, "insurer": path.stem, "text": chunk}))
            
        idx.upsert(vectors=batch)
        total += len(batch)
        logger.info(f"Indexed {len(batch)} chunks from {path.name}")
    return total

if __name__ == "__main__":
    run()
