import json
import re
from typing import Dict, List

from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import settings

# Initialize Gemini
gemini_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", api_key=settings.GEMINI_API_KEY)


def _extract_text(response) -> str:
    """
    Safely extract a string from whatever Gemini returns.
    If .text or .content is a method, call it.
    """
    # 1) If it has .text
    if hasattr(response, "text"):
        txt = response.text
        return txt() if callable(txt) else txt

    # 2) If it has .content
    if hasattr(response, "content"):
        cnt = response.content
        return cnt() if callable(cnt) else cnt

    # 3) Raw string
    if isinstance(response, str):
        return response

    # 4) LangChain-style .generations
    if hasattr(response, "generations"):
        gens = response.generations
        if isinstance(gens, list) and gens:
            first = gens[0]
            if hasattr(first, "text"):
                t = first.text
                return t() if callable(t) else t

    # 5) Fallback to str()
    return str(response)


def _parse_json(text: str) -> Dict:
    """
    Pull the first `{ ... }` JSON block out of `text` and parse it.
    """
    m = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not m:
        snippet = text.strip().replace("\n", " ")[:200]
        raise ValueError(f"No JSON object found in LLM response: {snippet}")
    json_str = m.group()
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        snippet = json_str.strip().replace("\n", " ")[:200]
        raise ValueError(f"Invalid JSON payload from LLM: {snippet}")


def structure_query(natural: str) -> Dict:
    """
    Parse a natural‐language insurance query into structured fields.
    """
    prompt = f"""
You receive an insurance‐claim query. Parse it and return JSON with the following keys:
- age (int, years, or null)
- procedure (string or null)
- location (string or null)
- policy_duration (string or null)

Original query: "{natural}"
Return *only* a JSON object.
"""
    raw = gemini_llm.invoke(prompt)
    text = _extract_text(raw)
    return _parse_json(text)


def synthesize_answer(natural: str, clauses: List[Dict]) -> Dict:
    """
    Given the original query and a list of retrieved clauses, produce
    a decision JSON with approval/rejection, amount, and justifications.
    Each justification must include:
      - clause_id
      - snippet (short extract)
      - full_text (complete clause text)
      - explanation (LLM’s reasoning in plain English)
    """
    contexts = "\n---\n".join(
        f"ID: {c['id']}\nFullText: {c['text']}"
        for c in clauses
    )
    prompt = f"""
You are an insurance‐claims specialist. Given the query:
“{natural}”

Use ONLY the following retrieved clauses to decide approval and justify in JSON.

Each clause is provided as:
ID: <clause_id>
FullText: <the entire clause text>

Return a single JSON object with keys:
1. decision: "approved" or "rejected"
2. amount: number or null
3. justification: an array of objects, each with:
   - clause_id: the ID you used above
   - snippet: a brief quoted excerpt from FullText
   - full_text: the entire clause text
   - explanation: your reasoning why this clause supports the decision

Do NOT include any other keys or commentary. Return STRICTLY valid JSON.
    
Relevant Clauses:
{contexts}
"""
    raw  = gemini_llm.invoke(prompt)
    text = _extract_text(raw)
    return _parse_json(text)


def chat_general(user_input: str) -> str:
    """
    Fallback general‐chat function that returns raw text.
    """
    raw = gemini_llm.invoke(user_input)
    return _extract_text(raw)
