import uuid
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session as DbSession
from src.models import Session, SessionTurn
from src.slots import REQUIRED_SLOTS

def create_session(db: DbSession, initial_state: Dict[str, Any] = None) -> Session:
    new_id = str(uuid.uuid4())
    session = Session(id=new_id, state=initial_state or {})
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def get_session(db: DbSession, session_id: str) -> Optional[Session]:
    return db.query(Session).filter(Session.id == session_id).first()

def update_session_state(db: DbSession, session_id: str, new_extracted_data: Dict[str, Any]) -> Session:
    session = get_session(db, session_id)
    if not session:
        return None
        
    # Merge dictionaries properly for JSON column update
    current_state = dict(session.state)
    for k, v in new_extracted_data.items():
        if v is not None:
            current_state[k] = v
            
    session.state = current_state
    
    # SQLAlchemy requires explicit flag to register JSON mutation sometimes, 
    # but reassignment works.
    from sqlalchemy.orm.attributes import flag_modified
    flag_modified(session, "state")
    
    db.commit()
    db.refresh(session)
    return session

def generate_clarifying_question(missing_slots: List[str], asked_questions: List[str]) -> str:
    """
    Generates a targeted clarifying question based on what's missing.
    Ensures we don't repeat the exact same question.
    """
    # Deterministic mapping as per rules (LLM picks the question based on missing vars)
    questions = {
        "rainfall": "Could you estimate the average annual rainfall (in mm) for this parcel?",
        "land_use": "What is the current primary land use (e.g., arable, pasture, orchard, forest)?"
    }
    
    for slot in missing_slots:
        q = questions.get(slot, f"Could you provide information about {slot}?")
        if q not in asked_questions:
            return q
            
    return "Could you provide more details about the environmental conditions?"

def record_turn(db: DbSession, session_id: str, user_input: str, system_response: str, trace: dict = None):
    turn = SessionTurn(
        session_id=session_id,
        user_input=user_input,
        system_response=system_response,
        retrieval_trace=trace or {}
    )
    db.add(turn)
    db.commit()
