import json
import asyncio
from uuid import uuid4
from tempfile import NamedTemporaryFile
from pathlib import Path

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
        async with httpx.AsyncClient(timeout=60) as client:
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

    vectors = await asyncio.to_thread(embed_texts, chunks)
    idx     = get_index()
    batch   = [
        (f"{request_id}-{i}", vec, {"source": s3_key, "insurer": request_id, "text": chunk})
        for i, (vec, chunk) in enumerate(zip(vectors, chunks))
    ]
    await asyncio.to_thread(idx.upsert, vectors=batch)
    logger.info(f"[{request_id}] upserted {len(batch)} chunks")

    sem = asyncio.Semaphore(2)

    async def answer_one(q: str) -> str:
        async with sem:
            ctxs = await asyncio.to_thread(retrieve, q, 10, request_id)
            context_str = "\n---\n".join(f"{c['source']}: {c['text']}…" for c in ctxs)

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
            return await asyncio.to_thread(chat_general, prompt)

    answers = await asyncio.gather(*(answer_one(q) for q in req.questions))
    return JSONResponse(
        status_code=200,
        content=AnswerResponse(answers=answers).dict()
    )
