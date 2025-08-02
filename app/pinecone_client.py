from pinecone import Pinecone, ServerlessSpec
from app.config import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
INDEX_NAME = "policy-retrieval"

def get_index():
    if not pc.has_index(INDEX_NAME):
        pc.create_index(
            name=INDEX_NAME,
            vector_type="dense",
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=settings.PINECONE_ENV),
            deletion_protection="disabled",
        )
    return pc.Index(INDEX_NAME)

index = get_index()
