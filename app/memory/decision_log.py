
from sqlalchemy.orm import Session

from app.memory.models import Decision
from app.retrieval.vector_store import VectorStore
from app.ingestion.embedder import Embedder


def create_decision(
    db: Session,
    question: str,
    answer: str,
    confidence: int,
    categories: str,
    sources: str,
    status: str = "approved",
):
    decision = Decision(
        question=question,
        answer=answer,
        confidence=confidence,
        categories=categories,
        sources=sources,
        status=status,
    )

    db.add(decision)
    db.commit()
    db.refresh(decision)

    return decision


def get_approved_decisions(db: Session):
    return (
        db.query(Decision)
        .filter(Decision.status == "approved")
        .order_by(Decision.created_at.desc())
        .all()
    )


def search_decisions(db: Session, query: str):
    search_term = f"%{query}%"

    return (
        db.query(Decision)
        .filter(
            Decision.status == "approved",
            Decision.question.ilike(search_term),
        )
        .order_by(Decision.created_at.desc())
        .all()
    )


def store_decision_in_vector_memory(decision):
    embedder = Embedder()
    vector_store = VectorStore(embedder)

    decision_text = (
        f"Question: {decision.question}\n"
        f"Answer: {decision.answer}\n"
        f"Categories: {decision.categories}\n"
        f"Sources: {decision.sources}\n"
        f"Status: {decision.status}"
    )

    metadata = {
        "source": "decision_memory",
        "decision_id": str(decision.id),
        "category": "decision",
        "status": decision.status,
    }

    vector_store.add_decision(
        decision_id=str(decision.id),
        text=decision_text,
        metadata=metadata,
    )


def get_pending_decisions(db: Session):
    return (
        db.query(Decision)
        .filter(Decision.status == "pending_review")
        .order_by(Decision.created_at.desc())
        .all()
    )


def approve_decision(db: Session, decision_id: int):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if decision is None:
        return None

    if decision.status == "approved":
        return decision

    decision.status = "approved"
    db.commit()
    db.refresh(decision)

    return decision


def reject_decision(db: Session, decision_id: int):
    decision = db.query(Decision).filter(
        Decision.id == decision_id
    ).first()

    if decision is None:
        return None

    decision.status = "rejected"
    db.commit()
    db.refresh(decision)

    return decision

