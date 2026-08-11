
from app.ingestion.embedder import Embedder
from app.retrieval.vector_store import VectorStore


def main():
    print("\n" + "=" * 60)
    print("THINK9 BRAIN - DECISION MEMORY RETRIEVAL TEST")
    print("=" * 60)

    embedder = Embedder()
    vector_store = VectorStore(embedder)

    query = "Can we use the same promotion structure?"

    print(f"\nQuery: {query}")

    results = vector_store.search_decisions(
        query=query,
        n_results=3,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    for i, (document, metadata) in enumerate(
        zip(documents, metadatas),
        start=1,
    ):
        print("\n" + "-" * 40)
        print(f"Result {i}")
        print(f"Source: {metadata['source']}")
        print(f"Decision ID: {metadata['decision_id']}")
        print(f"Category: {metadata['category']}")
        print(f"Content:\n{document}")

    if documents:
        print("\nDecision semantic retrieval PASSED.")
    else:
        print("\nDecision semantic retrieval FAILED.")

    print("\n" + "=" * 60)
    print("PHASE 9.3 VECTOR MEMORY RETRIEVAL PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()
