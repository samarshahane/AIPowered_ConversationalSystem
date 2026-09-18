from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DbSession
from typing import Dict, Any, List
import uuid

from src.models import InterventionCard
from src.schemas import ChatRequest, ChatResponse, AnalyzeRequest, TraceResponse
from src.slots import extract_slots, get_missing_slots
from src.session import create_session, get_session, update_session_state, generate_clarifying_question, record_turn
from src.rules import filter_cards
from src.scorer import score_cards, resolve_conflicts
from src.retrieval import query_corpus
from src.synthesis import synthesize_recommendations
from src.trace import build_trace
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import settings

router = APIRouter()

engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def dictify_card(c: InterventionCard) -> dict:
    return {
        "id": c.id,
        "name": c.name,
        "description": c.description,
        "preconditions": c.preconditions,
        "conflicts_with": c.conflicts_with,
        "effects": [
            {
                "metric_id": e.metric_id,
                "value_change": e.value_change,
                "time_horizon_years": e.time_horizon_years,
                "confidence_score": e.confidence_score,
                "source_id": e.source_id
            } for e in c.effects
        ]
    }

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: DbSession = Depends(get_db)):
    if request.session_id:
        session = get_session(db, request.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
    else:
        session = create_session(db, request.structured_inputs or {})

    new_slots = extract_slots(request.user_input)
    session = update_session_state(db, session.id, new_slots)
    
    missing = get_missing_slots(session.state)
    if missing:
        # Mocking asked history since we are not fully parsing turns for simplicity
        question = generate_clarifying_question(missing, [])
        record_turn(db, session.id, request.user_input, question)
        return ChatResponse(
            session_id=session.id,
            clarifying_question=question,
            message="I need more information before I can make a confident recommendation."
        )

    return process_analysis(db, session, request.user_input)

@router.post("/analyze", response_model=ChatResponse)
def analyze(request: AnalyzeRequest, db: DbSession = Depends(get_db)):
    session = create_session(db, request.state)
    return process_analysis(db, session, "Direct structured analysis")

def process_analysis(db: DbSession, session: Any, user_input: str) -> ChatResponse:
    db_cards = db.query(InterventionCard).all()
    all_cards = [dictify_card(c) for c in db_cards]
    
    passed_cards, rejections = filter_cards(all_cards, session.state)
    
    if not passed_cards:
        record_turn(db, session.id, user_input, "No interventions passed the constraints.")
        return ChatResponse(session_id=session.id, message="No interventions are suitable for these exact conditions.")
        
    scores = score_cards(passed_cards, session.state)
    final_cards = resolve_conflicts(passed_cards, scores)
    
    source_ids = list({effect["source_id"] for c in final_cards for effect in c["effects"]})
    
    evidence = []
    if source_ids:
        query_text = " ".join([c["name"] for c in final_cards])
        evidence = query_corpus(query_text, top_k=5, filter_source_ids=source_ids)
        
    recommendations = synthesize_recommendations(final_cards, evidence)
    
    trace_obj = build_trace(
        evaluated_cards_count=len(all_cards),
        passed_cards_count=len(passed_cards),
        rejections=rejections,
        scores=scores,
        retrieved_chunks=evidence
    )
    
    msg = f"Found {len(final_cards)} recommended interventions."
    record_turn(db, session.id, user_input, msg, trace_obj)
    
    return ChatResponse(
        session_id=session.id,
        recommendations=recommendations,
        message=msg
    )

@router.get("/trace/{session_id}", response_model=TraceResponse)
def get_trace(session_id: str, db: DbSession = Depends(get_db)):
    session = get_session(db, session_id)
    if not session or not session.turns:
        raise HTTPException(status_code=404, detail="Trace not found")
        
    latest_turn = session.turns[-1]
    trace = latest_turn.retrieval_trace or {}
    
    return TraceResponse(
        session_id=session_id,
        evaluated_cards=trace.get("evaluated_cards", 0),
        passed_cards=trace.get("passed_cards", 0),
        rejections=trace.get("rejections", []),
        scores=trace.get("scores", {}),
        retrieved_chunks=trace.get("retrieved_chunks", [])
    )
