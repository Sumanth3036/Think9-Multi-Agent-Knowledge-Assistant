
from app.memory.database import Base, SessionLocal, engine
from app.memory.decision_log import (
    create_decision,
    get_approved_decisions,
    search_decisions,
    store_decision_in_vector_memory,
)


def main():
    print("\n" + "=" * 60)
    print("THINK9 BRAIN - PHASE 9 MEMORY TEST")
    print("=" * 60)

    print("\nCreating database tables...")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        decision = create_decision(
            db=db,
            question="Can Brand A run a two-for-one promotion?",
            answer=(
                "Brand A can use a two-for-one promotion when "
                "the promotional terms are clearly displayed."
            ),
            confidence=91,
            categories="legal,brand",
            sources="legal_playbook.txt,brand_a_history.txt",
            status="approved",
        )

        print("\nDecision saved successfully.")
        print(f"ID: {decision.id}")
        print(f"Question: {decision.question}")
        print(f"Confidence: {decision.confidence}")
        print(f"Status: {decision.status}")

        # Store approved decision in ChromaDB
        if decision.status == "approved":
            store_decision_in_vector_memory(decision)
            print("\nDecision stored in ChromaDB memory.")

        decisions = get_approved_decisions(db)

        print("\nApproved decisions:")

        for item in decisions:
            print("\n" + "-" * 40)
            print(f"ID: {item.id}")
            print(f"Question: {item.question}")
            print(f"Answer: {item.answer}")
            print(f"Confidence: {item.confidence}")
            print(f"Categories: {item.categories}")
            print(f"Sources: {item.sources}")
            print(f"Status: {item.status}")

        print("\nSearching previous decisions...")

        results = search_decisions(
            db,
            "two-for-one promotion",
        )

        for item in results:
            print("\n" + "-" * 40)
            print(f"Found decision: {item.question}")
            print(f"Answer: {item.answer}")
            print(f"Status: {item.status}")

        if results:
            print("\nDecision memory search PASSED.")
        else:
            print("\nDecision memory search FAILED.")

        print("\n" + "=" * 60)
        print("PHASE 9.3 DATABASE + VECTOR MEMORY PASSED")
        print("=" * 60)

    finally:
        db.close()


if __name__ == "__main__":
    main()

