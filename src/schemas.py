from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    user_input: str
    structured_inputs: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    session_id: str
    clarifying_question: Optional[str] = None
    recommendations: Optional[List[Dict[str, Any]]] = None
    message: str

class AnalyzeRequest(BaseModel):
    session_id: Optional[str] = None
    state: Dict[str, Any]

class TraceResponse(BaseModel):
    session_id: str
    evaluated_cards: int
    passed_cards: int
    rejections: List[Dict[str, str]]
    scores: Dict[str, float]
    retrieved_chunks: List[Dict[str, Any]]
