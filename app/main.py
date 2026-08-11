"""FastAPI entry point for Think9 Brain."""

import logging

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app.memory.database import Base, SessionLocal, engine
from app.memory import models  # Registers Decision with SQLAlchemy metadata.
from app.models.schemas import DecisionResponse, ReviewQueueResponse, VerifyRequest

app = FastAPI(title="Think9 Brain")
Base.metadata.create_all(bind=engine)
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def serialize_decision(decision):
    return {
        "question": decision.question,
        "answer": decision.answer,
        "confidence": decision.confidence,
        "categories": [item for item in decision.categories.split(",") if item],
        "sources": [item for item in decision.sources.split(",") if item],
        "status": decision.status,
        "review_required": decision.status == "pending_review",
        "decision_id": decision.id,
    }


@app.get("/")
def health():
    return {"status": "running", "service": "Think9 Brain"}


@app.post("/verify", response_model=DecisionResponse)
def verify(request: VerifyRequest, db: Session = Depends(get_db)):
    try:
        from app.graph import run_workflow
        return run_workflow(request.question.strip(), db)
    except HTTPException:
        raise
    except Exception as exc:
        # Keep the client response safe, while preserving the original traceback
        # in the server log for operational diagnosis.
        logger.exception("Verification workflow failed")
        raise HTTPException(status_code=503, detail="Unable to verify the question at this time.") from exc


@app.get("/review", response_model=ReviewQueueResponse)
def review_queue(db: Session = Depends(get_db)):
    try:
        from app.memory.decision_log import get_pending_decisions
        return {"decisions": [
            serialize_decision(item) for item in get_pending_decisions(db)
        ]}
    except Exception as exc:
        logger.exception("Review queue lookup failed")
        raise HTTPException(status_code=503, detail="Unable to load the review queue.") from exc


@app.post("/review/{decision_id}/approve", response_model=DecisionResponse)
def approve_review(decision_id: int, db: Session = Depends(get_db)):
    try:
        from app.memory.decision_log import (
            approve_decision,
            store_decision_in_vector_memory,
        )
        decision = approve_decision(db, decision_id)
        if decision is None:
            raise HTTPException(status_code=404, detail="Decision not found.")
        store_decision_in_vector_memory(decision)
        return serialize_decision(decision)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Decision approval failed for decision_id=%s", decision_id)
        raise HTTPException(status_code=503, detail="Unable to approve the decision.") from exc


@app.post("/review/{decision_id}/reject", response_model=DecisionResponse)
def reject_review(decision_id: int, db: Session = Depends(get_db)):
    try:
        from app.memory.decision_log import reject_decision
        decision = reject_decision(db, decision_id)
        if decision is None:
            raise HTTPException(status_code=404, detail="Decision not found.")
        return serialize_decision(decision)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Decision rejection failed for decision_id=%s", decision_id)
        raise HTTPException(status_code=503, detail="Unable to reject the decision.") from exc
