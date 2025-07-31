# from pinecone import Pinecone, ServerlessSpec
# from app.config import settings

# pc = Pinecone(api_key=settings.PINECONE_API_KEY)
# INDEX_NAME = "policy-retrieval"

# def get_index():
#     if not pc.has_index(INDEX_NAME):
#         pc.create_index(
#             name=INDEX_NAME,
#             vector_type="dense",
#             dimension=768,
#             metric="cosine",
#             spec=ServerlessSpec(cloud="aws", region=settings.PINECONE_ENV),
#             deletion_protection="disabled",
#         )
#     return pc.Index(INDEX_NAME)

# index = get_index()

# app/pinecone_client.py
from pinecone import Pinecone, ServerlessSpec
from app.config import settings

# Instantiate Pinecone client
pc = Pinecone(
    api_key=settings.PINECONE_API_KEY,
    environment=settings.PINECONE_ENV  # e.g. "us-west1-gcp"
)

INDEX_NAME = "policy-retrieval"


def get_index():
    """
    Get or create the Pinecone index for policy retrieval.
    """
    # Create the index if it does not exist
    existing = pc.list_indexes().names()
    if INDEX_NAME not in existing:
        pc.create_index(
            name=INDEX_NAME,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region=settings.PINECONE_ENV)
        )
    # Return the index client
    return pc.Index(INDEX_NAME)


# Convenience instance for direct use
index = get_index()