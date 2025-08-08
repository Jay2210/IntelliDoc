import json
import asyncio
from uuid import uuid4
from tempfile import NamedTemporaryFile
from pathlib import Path
import time

import httpx
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Body,
)
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware

from app.schemas import MultiQuestionRequest, AnswerResponse
from app.llm import chat_general
from app.retriever import retrieve
from app.s3_storage import _bucket
from app.docs_loader import load_document
from app.chunking import chunk_text
from app.embeddings import embed_texts
from app.pinecone_client import get_index
from app.utils import get_logger

logger = get_logger(__name__)

app = FastAPI(title="HackRx Policy Q&R")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BEARER_TOKEN = "9209d3d55da6a5973a019141c4ca292676a7cbf5d45890572c3f88b9c8bb911d"
bearer_scheme = HTTPBearer()

def verify_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    if credentials.scheme.lower() != "bearer" or credentials.credentials != BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing bearer token"
        )
@app.post(
    "/hackrx/run",
    response_model=AnswerResponse,
    summary="Run a multi-question query on a single document URL",
    dependencies=[Depends(verify_bearer_token)],
)
async def run(req: MultiQuestionRequest = Body(
    ...,
    example={
      "documents": "",
      "questions": []
    }
)):
    request_id = uuid4().hex

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.get(req.documents, follow_redirects=True)
            r.raise_for_status()
        pdf_bytes = r.content
        logger.info(f"[{request_id}] downloaded {len(pdf_bytes)} bytes")
    except Exception as e:
        logger.error(f"[{request_id}] download error: {e}")
        raise HTTPException(400, f"Failed to fetch document: {e}")

    s3_key = f"documents/{request_id}.pdf"
    try:
        await asyncio.to_thread(_bucket.put_object, Key=s3_key, Body=pdf_bytes)
        logger.info(f"[{request_id}] uploaded PDF to S3 at {s3_key}")
    except Exception as e:
        logger.error(f"[{request_id}] S3 upload error: {e}")
        raise HTTPException(500, "Failed to push PDF to S3")

    with NamedTemporaryFile(suffix=".pdf") as tmpf:
        tmpf.write(pdf_bytes)
        tmpf.flush()
        text   = await asyncio.to_thread(load_document, Path(tmpf.name))
        chunks = await asyncio.to_thread(chunk_text, text)

    vectors = await asyncio.to_thread(embed_texts, chunks, task="retrieval.passage")
    idx     = get_index()
    
    try:
        initial_stats = await asyncio.to_thread(idx.describe_index_stats)
        initial_vector_count = initial_stats.get("total_vector_count", 0)
    except Exception as e:
        logger.warning(f"Could not get initial index stats: {e}. Defaulting count to 0.")
        initial_vector_count = 0

    # 2. Upsert the new vectors
    batch   = [
        (f"{request_id}-{i}", vec, {"source": s3_key, "insurer": request_id, "text": chunk})
        for i, (vec, chunk) in enumerate(zip(vectors, chunks))
    ]
    await asyncio.to_thread(idx.upsert, vectors=batch)
    logger.info(f"[{request_id}] upserted {len(batch)} chunks")

    # 3. Poll the index until the vector count is updated
    expected_count = initial_vector_count + len(batch)
    timeout_seconds = 5
    start_time = time.monotonic()
    
    logger.info(f"[{request_id}] Waiting for index to update to {expected_count} vectors...")
    
    while (time.monotonic() - start_time) < timeout_seconds:
        try:
            stats = await asyncio.to_thread(idx.describe_index_stats)
            current_count = stats.get("total_vector_count", 0)
            if current_count >= expected_count:
                logger.info(f"[{request_id}] Index is ready with {current_count} vectors.")
                break
            else:
                logger.info(f"[{request_id}] Current vector count: {current_count}. Waiting...")
        except Exception as e:
            logger.warning(f"Polling failed with error: {e}. Retrying...")

        await asyncio.sleep(1.5) # Wait before the next check
    else: # This runs if the while loop finishes without a 'break'
        logger.warning(f"[{request_id}] Index update timed out after {timeout_seconds}s. Proceeding anyway.")

    sem = asyncio.Semaphore(2)

    async def answer_one(q: str) -> str:
        async with sem:
            ctxs = await asyncio.to_thread(retrieve, q, 5, request_id)
            context_str = "\n---\n".join(f"{c['source']}: {c['text']}…" for c in ctxs)

        prompt = f"""
You are a highly precise question-answering assistant. The context snippets may come from insurance policies, constitutions, books, or any other document. Answer the user’s question **only** using the information in these snippets.

Instructions:
1. Read all CONTEXT snippets and identify the single most relevant passage.
2. Extract every key detail you need to answer:
   - If it’s a policy: conditions, waiting periods, limits/sub-limits, definitions, coverage type.
   - If it’s legal text or a book: factual assertions, definitions, dates, names, or any explicit statement.
3. Compose your answer in **at most two sentences**:
   - **Sentence 1:** Directly answer the question (Yes/No or factual statement).
   - **Sentence 2 (if needed):** Qualifying details or elaboration.
   - When you mention durations or amounts, include both word and numeric forms (e.g. “thirty-six (36) months”).
   - Do **not** use lists, bullets, or formatting—just plain text.
4. **Missing details:** If the context does **not** contain a required piece of information, say  
   “The context does not specify the <detail>.”

---
CONTEXT:
{context_str}
---
QUESTION: {q}

ANSWER:
"""
        return await asyncio.to_thread(chat_general, prompt)

    answers = await asyncio.gather(*(answer_one(q) for q in req.questions))
    return JSONResponse(
        status_code=200,
        content=AnswerResponse(answers=answers).dict()
    )
