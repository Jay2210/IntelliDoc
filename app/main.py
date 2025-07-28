from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from uuid import uuid4
from pathlib import Path

from app.schemas import (
    QueryRequest,
    QueryResponse,
    GeneralResponse,
    QueryLog
)
from app.llm import (
    structure_query,
    synthesize_answer,
    chat_general
)
from app.retriever import retrieve
from app.s3_storage import save_json
from app.docs_loader import load_document
from app.chunking import chunk_text
from app.embeddings import embed_texts
from app.pinecone_client import get_index
from app.utils import get_logger
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HackRx Policy Q&R")
logger = get_logger(__name__)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allows your React app to connect
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/query")
async def query_endpoint(req: QueryRequest):
    """
    Unified endpoint:
    - If the query yields ≥2 structured fields *and* returns >0 clauses, do structured synthesis.
    - Otherwise, fall back to general Q&A chat with Pinecone context.
    """
    req.request_id = req.request_id or uuid4().hex
    insurer = req.insurer  # may be None

    # 1) Parse into structured fields
    params = structure_query(req.query)

    # 2) If more than 2 of the 4 fields are missing, fallback
    missing = sum(1 for v in params.values() if not v)
    if missing > 2:
        return await _fallback(req, insurer)

    # 3) Retrieve clauses scoped by insurer if provided
    combined = " ".join(str(v) for v in params.values() if v)
    clauses  = retrieve(combined, top_k=5, insurer=insurer)

    # 4) If we parsed enough fields but found zero clauses, still fallback
    if not clauses:
        return await _fallback(req, insurer)

    # 5) Structured synthesis
    structured = synthesize_answer(req.query, clauses)
    response   = QueryResponse(**structured)

    # 6) Log and return structured result
    save_json(f"logs/{req.request_id}.json", {
        "request_id": req.request_id,
        "query":       req.query,
        "response":    response.dict(),
    })
    return response


async def _fallback(req: QueryRequest, insurer: str):
    """
    Pull context snippets (filtered by insurer if given) then
    use chat_general to answer in free‐form text.
    """
    logger.info(f"[{req.request_id}] falling back to general chat")

    contexts = retrieve(req.query, top_k=10, insurer=insurer)
    context_str = "\n---\n".join(
        f"{c['source']} ({c['id']}): {c['text'][:200]}…"
        for c in contexts
    )

    prompt = (
        "Use the following context snippets to answer the question:\n"
        f"{context_str}\n\n"
        f"Question: {req.query}"
    )
    answer = chat_general(prompt)
    general_resp = GeneralResponse(answer=answer)

    # Log the fallback as well
    save_json(f"logs/{req.request_id}.json", {
        "request_id": req.request_id,
        "query":       req.query,
        "response":    general_resp.dict(),
    })

    return JSONResponse(status_code=200, content=general_resp.dict())


@app.post("/upload", status_code=201)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a document (PDF, DOCX, EML) and immediately index its chunks into Pinecone.
    Returns the filename and number of chunks indexed.
    """
    docs_dir = Path("data/docs")
    docs_dir.mkdir(parents=True, exist_ok=True)

    file_path = docs_dir / file.filename
    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    logger.info(f"Saved uploaded file: {file_path}")

    text = load_document(file_path)
    chunks = chunk_text(text)
    vectors = embed_texts(chunks)

    idx = get_index()
    batch = []
    for i, (vec, chunk) in enumerate(zip(vectors, chunks)):
       batch.append((
           f"{file_path.stem}-{i}", 
           vec,
           {
             "source":   file.filename,
             "insurer":  file_path.stem,
             "text":     chunk
           }
       ))
    idx.upsert(vectors=batch)
    logger.info(f"Indexed {len(batch)} chunks from {file.filename}")

    return {"filename": file.filename, "indexed_chunks": len(batch)}


@app.post("/ingest")
async def ingest_endpoint():
    """
    One-off: load all files under data/docs into Pinecone.
    Returns how many chunks were indexed.
    """
    from scripts.index_documents import run as index_run
    count = index_run()
    return {"indexed_chunks": count}
