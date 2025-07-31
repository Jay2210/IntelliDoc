from typing import List, Optional
from pydantic import BaseModel

class QueryRequest(BaseModel):
    request_id: Optional[str] = None
    query: str
    insurer: Optional[str] = None    
    policy_id: Optional[str] = None 

class Clause(BaseModel):
    id: str
    source: str
    text: str
    score: float

class Justification(BaseModel):
    clause_id: str
    snippet: str
    full_text: str        # the entire clause text
    explanation: str      # LLM reasoning why this clause applies

class QueryResponse(BaseModel):
    decision: str
    amount: Optional[float]
    justification: List[Justification]

class GeneralResponse(BaseModel):
    answer: str

class QueryLog(BaseModel):
    request_id: str
    query: str
    response: dict  # could be QueryResponse or GeneralResponse

class MultiQuestionRequest(BaseModel):
    documents: str
    questions: List[str]
    
class AnswerResponse(BaseModel):
    answers: List[str]