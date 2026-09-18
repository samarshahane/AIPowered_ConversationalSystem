from sqlalchemy import Column, Integer, String, Float, ForeignKey, Boolean, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Source(Base):
    __tablename__ = "sources"
    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=True)
    author = Column(String, nullable=True)
    year = Column(Integer, nullable=True)

class Metric(Base):
    __tablename__ = "metrics"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    description = Column(Text, nullable=True)

class InterventionCard(Base):
    __tablename__ = "intervention_cards"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    preconditions = Column(JSON, nullable=False) # e.g. {"min_rainfall": 500, "max_ph": 8.0}
    conflicts_with = Column(JSON, nullable=True) # list of card IDs

    effects = relationship("InterventionEffect", back_populates="card")

class InterventionEffect(Base):
    __tablename__ = "intervention_effects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    card_id = Column(String, ForeignKey("intervention_cards.id"))
    metric_id = Column(String, ForeignKey("metrics.id"))
    source_id = Column(String, ForeignKey("sources.id"))
    
    value_change = Column(Float, nullable=False) # e.g. +15.0 for 15% increase
    time_horizon_years = Column(Float, nullable=False)
    confidence_score = Column(Float, nullable=False) # 0.0 to 1.0
    
    card = relationship("InterventionCard", back_populates="effects")
    metric = relationship("Metric")
    source = relationship("Source")

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    state = Column(JSON, nullable=False, default={}) # Extracted variables
    
    turns = relationship("SessionTurn", back_populates="session", order_by="SessionTurn.created_at")

class SessionTurn(Base):
    __tablename__ = "session_turns"
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    user_input = Column(Text, nullable=True)
    system_response = Column(Text, nullable=True)
    retrieval_trace = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="turns")
