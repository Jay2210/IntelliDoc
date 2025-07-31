from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from typing import List, Optional
from fastapi.responses import JSONResponse
from uuid import uuid4
from pathlib import Path
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
import httpx


from schemas import (
    QueryRequest,
    QueryResponse,
    GeneralResponse,
    QueryLog,
    MultiQuestionRequest,
    AnswerResponse
)
from app.llm import (
    structure_query,
    synthesize_answer,
    chat_general
)
from retriever import retrieve
from s3_storage import save_json
from docs_loader import load_document
from chunking import chunk_text
from embeddings import embed_texts
from pinecone_client import get_index
from utils import get_logger
from fastapi.middleware.cors import CORSMiddleware

import asyncio
import json
from fastapi.concurrency import run_in_threadpool

app = FastAPI(title="HackRx Policy Q&R")
logger = get_logger(__name__)

bearer_scheme = HTTPBearer()

def require_api_key(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
):
    token = credentials.credentials
    if token != "9209d3d55da6a5973a019141c4ca292676a7cbf5d45890572c3f88b9c8bb911d":
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows your React app to connect  
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
    insurer = req.insurer

    params = structure_query(req.query)

    missing = sum(1 for v in params.values() if not v)
    if missing > 2:
        return await _fallback(req, insurer)
    combined = " ".join(str(v) for v in params.values() if v)
    clauses  = retrieve(combined, top_k=5, insurer=insurer)

    if not clauses:
        return await _fallback(req, insurer)

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

    contexts = retrieve(req.query, top_k=50, insurer=insurer)
    context_str = "\n---\n".join(
        f"{c['source']} ({c['id']}): {c['text'][:500]}…"
        f"{c['source']} ({c['id']}): {c['text'][:500]}…"
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

@app.post(
    "/run",
    response_model=AnswerResponse,
    summary="Run a multi-question query on a single document",
    dependencies=[Depends(require_api_key)]
)
async def run(
    file: UploadFile = File(...),
    questions: List[str] = Form(...),
):
    request_id = uuid4().hex
    filename = file.filename

    # 1) Save the file locally
    docs_dir = Path("data/docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    local_path = docs_dir / f"{request_id}-{filename}"
    contents = await file.read()
    local_path.write_bytes(contents)
    logger.info(f"[{request_id}] saved upload to {local_path}")

    # 2) Load, chunk, embed, and upsert *with* a custom 'insurer' tag = our request_id
    text = load_document(local_path)
    chunks = chunk_text(text)
    vectors = embed_texts(chunks)
    idx = get_index()
    batch = [
        (
            f"{request_id}-{i}",
            vec,
            {
                "source": filename,
                "insurer": request_id,     # <— tag every chunk with this run’s ID
                "text": chunk,
            },
        )
        for i, (vec, chunk) in enumerate(zip(vectors, chunks))
    ]
    idx.upsert(vectors=batch)
    logger.info(f"[{request_id}] upserted {len(batch)} chunks")

    # 3) Normalize the questions field (JSON-array string, comma-sep, or multiple -F)
    raw = questions[0].strip() if len(questions) == 1 else None
    if len(questions) == 1 and raw and raw.startswith("["):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list) and all(isinstance(q, str) for q in parsed):
                qs = parsed
            else:
                qs = questions
        except json.JSONDecodeError:
            qs = questions
    elif len(questions) == 1 and raw and "," in raw:
        qs = [q.strip() for q in raw.split(",") if q.strip()]
    else:
        qs = questions

    if not qs:
        raise HTTPException(400, detail="No valid questions provided")

    # 4) Answer each question in parallel (max 2 concurrent), but *filter* by our request_id
    sem = asyncio.Semaphore(2)

    async def answer_one(q: str) -> str:
        async with sem:
            # only retrieve chunks where metadata.insurer == request_id
            ctxs = retrieve(q, top_k=50, insurer=request_id)
            context_str = "\n---\n".join(
                f"{c['source']}: {c['text'][:200]}…" for c in ctxs
            )
            prompt = (
                "You are an expert insurance-policy analyst.\n"
            "Using **only** the context snippets below, answer the question in **complete, audit-ready sentences**.\n"
            "Include durations, numeric values, conditions, and any limits exactly as they appear.\n\n"
            f"Context:\n{context_str}\n\n"
            f"Question: {q}\n\nAnswer:"
            )
            try:
                return await run_in_threadpool(lambda: chat_general(prompt))
            except Exception as e:
                logger.error(f"[{request_id}] error on “{q}”: {e}")
                return f"Error answering '{q}': {e}"

    tasks = [answer_one(q) for q in qs]
    answers = await asyncio.gather(*tasks)

    return AnswerResponse(answers=answers)
@app.post(
    "/run",
    response_model=AnswerResponse,
    summary="Run a multi-question query on a single document",
    dependencies=[Depends(require_api_key)]
)
async def run(
    file: UploadFile = File(...),
    questions: List[str] = Form(...),
):
    request_id = uuid4().hex
    filename = file.filename

    # 1) Save the file locally
    docs_dir = Path("data/docs")
    docs_dir.mkdir(parents=True, exist_ok=True)
    local_path = docs_dir / f"{request_id}-{filename}"
    contents = await file.read()
    local_path.write_bytes(contents)
    logger.info(f"[{request_id}] saved upload to {local_path}")

    text = load_document(local_path)
    chunks = chunk_text(text)
    vectors = embed_texts(chunks)
    idx = get_index()
    batch = [
        (
            f"{request_id}-{i}",
            vec,
            {
                "source": filename,
                "insurer": request_id,     
                "text": chunk,
            },
        )
        for i, (vec, chunk) in enumerate(zip(vectors, chunks))
    ]
    idx.upsert(vectors=batch)
    logger.info(f"[{request_id}] upserted {len(batch)} chunks")

    raw = questions[0].strip() if len(questions) == 1 else None
    if len(questions) == 1 and raw and raw.startswith("["):
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, list) and all(isinstance(q, str) for q in parsed):
                qs = parsed
            else:
                qs = questions
        except json.JSONDecodeError:
            qs = questions
    elif len(questions) == 1 and raw and "," in raw:
        qs = [q.strip() for q in raw.split(",") if q.strip()]
    else:
        qs = questions

    if not qs:
        raise HTTPException(400, detail="No valid questions provided")

    sem = asyncio.Semaphore(2)

    async def answer_one(q: str) -> str:
        async with sem:

            ctxs = retrieve(q, top_k=10, insurer=request_id)
            context_str = "\n---\n".join(
                f"{c['source']}: {c['text']}…" for c in ctxs
            )
            prompt = f"""
You are a meticulous and detail-oriented insurance policy analyst. Your task is to answer the user's question with maximum precision and completeness, based *only* on the provided context snippets.

Follow these instructions exactly:
1.  **Analyze the Context:** Carefully read all the provided context snippets to find the most relevant clauses that answer the user's question.
2.  **Extract All Details:** From the relevant clauses, you must extract every key detail. Pay close attention to the following, and list them if they are present:
    * **Conditions and Eligibility:** What are the specific requirements, waiting periods, age limits, or pre-requisites?
    * **Limits and Sub-limits:** Are there any monetary caps, percentage-based limits, or limits on frequency (e.g., "up to 2 deliveries")?
    * **Specific Criteria:** For definitions (like "Hospital"), what are all the specific criteria listed (e.g., bed count, staff requirements, facilities)?
    * **Type of Coverage:** Is the coverage for "in-patient," "out-patient," "day care," etc.?
3.  **Synthesize the Answer:**
    * Start with a direct, one-sentence answer (e.g., "Yes, this is covered," "No, this is excluded," "The waiting period is X months.").
    * Answer should be at max 2 lines. 1st Line should have the answer yes/no and the duration or any other important detail. 2nd Line should have details if necessary.
    * Do no formatting, just plain text. 
4.  **Handle Missing Information:** If a specific detail is not mentioned in the context, you must explicitly state that (e.g., "* The context does not specify the maximum number of deliveries.").

---
CONTEXT:
{context_str}
---
QUESTION: {q}

ANSWER:
"""
            try:
                return await run_in_threadpool(lambda: chat_general(prompt))
            except Exception as e:
                logger.error(f"[{request_id}] error on “{q}”: {e}")
                return f"Error answering '{q}': {e}"

    tasks = [answer_one(q) for q in qs]
    answers = await asyncio.gather(*tasks)

    return AnswerResponse(answers=answers)