from typing import List
from sentence_transformers import SentenceTransformer

# Load a SentenceTransformer model; returns 1536-dim embeddings by default
_model = SentenceTransformer("all-mpnet-base-v2")

def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Embed a list of texts into vectors.
    Returns a list of list-of-floats (batch_size x 1536).
    """
    # encode defaults to convert_to_numpy=True, returning a numpy array
    embeddings = _model.encode(texts)
    # convert to plain Python lists
    return embeddings.tolist()
