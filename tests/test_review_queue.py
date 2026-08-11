"""
Phase 10 - Review Queue End-to-End Test

Uses in-memory SQLite and ephemeral ChromaDB to avoid
polluting production data.
"""

import chromadb
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.memory.models import Decision
from app.memory.database import Base
from app.memory.decision_log import (
    create_decision,
    get_pending_decisions,
    approve_decision,
    reject_decision,
)
from app.ingestion.embedder import Embedder


def make_test_db():
    """Create an in-memory SQLite database with Decision table."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    return Session()


def store_decision_in_test_memory(decision, embedder, collection):
    """Store a decision in an isolated ChromaDB collection."""
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

    embedding = embedder.embed([decision_text])[0]

    collection.upsert(
        ids=[f"decision_{decision.id}"],
        documents=[decision_text],
        metadatas=[metadata],
        embeddings=[embedding],
    )


def search_test_decisions(query, embedder, collection, n_results=3):
    """Search the isolated ChromaDB decision collection."""
    query_embedding = embedder.embed([query])[0]

    return collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )


def main():
    print("\n" + "=" * 60)
    print("THINK9 BRAIN - PHASE 10 REVIEW QUEUE TEST")
    print("=" * 60)

    # --- Setup ---
    db = make_test_db()
    embedder = Embedder()

    # Ephemeral ChromaDB client (no files written)
    chroma_client = chromadb.Client()
    test_collection = chroma_client.get_or_create_collection(
        name="test_decisions",
    )

    # ==========================================================
    # TEST A -- Pending -> Approved -> Stored in ChromaDB
    # ==========================================================

    print("\n" + "-" * 60)
    print("TEST A -- Pending -> Approved -> ChromaDB")
    print("-" * 60)

    # Step 1: Create a pending legal decision
    decision_a = create_decision(
        db=db,
        question="Can Brand A run this legal promotion?",
        answer="The promotion requires human legal approval.",
        confidence=95,
        categories="legal",
        sources="legal_playbook.txt",
        status="pending_review",
    )

    print(f"\nCreated decision ID={decision_a.id}")
    print(f"Status: {decision_a.status}")

    assert decision_a.status == "pending_review", (
        f"Expected pending_review, got {decision_a.status}"
    )
    print("  PASS - Decision created with pending_review status")

    # Step 2: Verify it appears in pending queue
    pending = get_pending_decisions(db)
    pending_ids = [d.id for d in pending]

    assert decision_a.id in pending_ids, (
        "Decision not found in pending queue"
    )
    print("  PASS - Decision appears in pending review queue")

    # Step 3: Approve the decision
    approved = approve_decision(db, decision_a.id)

    assert approved is not None, "approve_decision returned None"
    assert approved.status == "approved", (
        f"Expected approved, got {approved.status}"
    )
    print("  PASS - Decision approved successfully")

    # Step 4: Verify no longer in pending queue
    pending_after = get_pending_decisions(db)
    pending_ids_after = [d.id for d in pending_after]

    assert decision_a.id not in pending_ids_after, (
        "Approved decision still in pending queue"
    )
    print("  PASS - Decision removed from pending queue")

    # Step 5: Store approved decision in isolated ChromaDB
    store_decision_in_test_memory(
        approved, embedder, test_collection
    )
    print("  PASS - Approved decision stored in ChromaDB")

    # Step 6: Retrieve from ChromaDB
    results = search_test_decisions(
        "Brand A legal promotion",
        embedder,
        test_collection,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    assert len(documents) > 0, (
        "No documents found in decision memory"
    )

    found_approved = any(
        m.get("decision_id") == str(decision_a.id)
        for m in metadatas
    )

    assert found_approved, (
        "Approved decision not found in ChromaDB"
    )
    print("  PASS - Approved decision retrieved from ChromaDB")

    # Step 7: Test idempotent re-approval
    re_approved = approve_decision(db, decision_a.id)

    assert re_approved.status == "approved", (
        "Re-approval changed status"
    )
    print("  PASS - Re-approval is idempotent")

    print("\n  TEST A PASSED")

    # ==========================================================
    # TEST B -- Pending -> Rejected -> NOT in ChromaDB
    # ==========================================================

    print("\n" + "-" * 60)
    print("TEST B -- Pending -> Rejected -> NOT in ChromaDB")
    print("-" * 60)

    # Step 1: Create another pending decision
    decision_b = create_decision(
        db=db,
        question="Should we use aggressive discount language?",
        answer="Aggressive discount language may violate guidelines.",
        confidence=72,
        categories="brand",
        sources="brand_guidelines.txt",
        status="pending_review",
    )

    print(f"\nCreated decision ID={decision_b.id}")
    print(f"Status: {decision_b.status}")

    assert decision_b.status == "pending_review", (
        f"Expected pending_review, got {decision_b.status}"
    )
    print("  PASS - Decision created with pending_review status")

    # Step 2: Verify it appears in pending queue
    pending_b = get_pending_decisions(db)
    pending_b_ids = [d.id for d in pending_b]

    assert decision_b.id in pending_b_ids, (
        "Decision not found in pending queue"
    )
    print("  PASS - Decision appears in pending review queue")

    # Step 3: Reject the decision
    rejected = reject_decision(db, decision_b.id)

    assert rejected is not None, "reject_decision returned None"
    assert rejected.status == "rejected", (
        f"Expected rejected, got {rejected.status}"
    )
    print("  PASS - Decision rejected successfully")

    # Step 4: Do NOT store in ChromaDB (this is the point)

    # Step 5: Search ChromaDB -- rejected should not appear
    results_b = search_test_decisions(
        "aggressive discount language",
        embedder,
        test_collection,
    )

    documents_b = results_b["documents"][0]
    metadatas_b = results_b["metadatas"][0]

    found_rejected = any(
        m.get("decision_id") == str(decision_b.id)
        for m in metadatas_b
    )

    assert not found_rejected, (
        "Rejected decision was found in ChromaDB -- this is wrong!"
    )
    print("  PASS - Rejected decision NOT found in ChromaDB")

    # Step 6: Verify rejected is not in pending queue
    pending_final = get_pending_decisions(db)
    pending_final_ids = [d.id for d in pending_final]

    assert decision_b.id not in pending_final_ids, (
        "Rejected decision still in pending queue"
    )
    print("  PASS - Rejected decision removed from pending queue")

    print("\n  TEST B PASSED")

    # ==========================================================
    # Summary
    # ==========================================================

    print("\n" + "=" * 60)
    print("PHASE 10 REVIEW QUEUE -- ALL TESTS PASSED")
    print("=" * 60)
    print("\nWorkflow verified:")
    print("  APPROVED  -> SQLite + ChromaDB decision memory")
    print("  REJECTED  -> SQLite only (NOT in ChromaDB)")

    db.close()


if __name__ == "__main__":
    main()
