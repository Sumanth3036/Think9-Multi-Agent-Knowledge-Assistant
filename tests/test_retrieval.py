"""
Phase 4 — Retrieval Tests

Verifies that ChromaDB returns the correct documents
for different queries and category filters.
"""

from app.ingestion.embedder import Embedder
from app.retrieval.vector_store import VectorStore


def test_legal_query():
    """
    Ask about two-for-one promotions.
    Expect: legal_playbook.txt should be the top result.
    """
    print("=" * 60)
    print("TEST 1: Legal query")
    print("Query: What are the rules for two-for-one promotions?")
    print("=" * 60)

    embedder = Embedder()
    store = VectorStore(embedder)

    results = store.search(
        query="What are the rules for two-for-one promotions?",
        n_results=3,
    )

    print()
    for i, (doc, meta) in enumerate(
        zip(results["documents"][0], results["metadatas"][0])
    ):
        print(f"  Result {i + 1}:")
        print(f"    Source:   {meta['source']}")
        print(f"    Category: {meta['category']}")
        print(f"    Preview:  {doc[:120]}...")
        print()

    top_source = results["metadatas"][0][0]["source"]
    assert top_source == "legal_playbook.txt", (
        f"Expected legal_playbook.txt, got {top_source}"
    )
    print("  PASSED — top result is legal_playbook.txt\n")


def test_brand_a_query():
    """
    Ask about Brand A's previous promotion.
    Expect: brand_a_history.txt should be the top result.
    """
    print("=" * 60)
    print("TEST 2: Brand A query")
    print("Query: What happened with Brand A's previous promotion?")
    print("=" * 60)

    embedder = Embedder()
    store = VectorStore(embedder)

    results = store.search(
        query="What happened with Brand A's previous promotion?",
        n_results=3,
    )

    print()
    for i, (doc, meta) in enumerate(
        zip(results["documents"][0], results["metadatas"][0])
    ):
        print(f"  Result {i + 1}:")
        print(f"    Source:   {meta['source']}")
        print(f"    Category: {meta['category']}")
        print(f"    Preview:  {doc[:120]}...")
        print()

    top_source = results["metadatas"][0][0]["source"]
    assert top_source == "brand_a_history.txt", (
        f"Expected brand_a_history.txt, got {top_source}"
    )
    print("  PASSED — top result is brand_a_history.txt\n")


def test_category_filter_legal():
    """
    Search with category='legal' filter.
    Expect: ALL results should have category='legal'.
    """
    print("=" * 60)
    print("TEST 3: Category filter — legal only")
    print("Query: What does the documentation say?")
    print("Filter: category = legal")
    print("=" * 60)

    embedder = Embedder()
    store = VectorStore(embedder)

    results = store.search(
        query="What does the documentation say?",
        n_results=5,
        category="legal",
    )

    print()
    for i, (doc, meta) in enumerate(
        zip(results["documents"][0], results["metadatas"][0])
    ):
        print(f"  Result {i + 1}:")
        print(f"    Source:   {meta['source']}")
        print(f"    Category: {meta['category']}")
        print(f"    Preview:  {doc[:120]}...")
        print()

    for meta in results["metadatas"][0]:
        assert meta["category"] == "legal", (
            f"Expected category='legal', got '{meta['category']}'"
        )
    print("  PASSED — all results are from category 'legal'\n")


def test_category_filter_brand():
    """
    Search with category='brand' filter.
    Expect: ALL results should have category='brand'.
    """
    print("=" * 60)
    print("TEST 4: Category filter — brand only")
    print("Query: What is the brand positioning strategy?")
    print("Filter: category = brand")
    print("=" * 60)

    embedder = Embedder()
    store = VectorStore(embedder)

    results = store.search(
        query="What is the brand positioning strategy?",
        n_results=5,
        category="brand",
    )

    print()
    for i, (doc, meta) in enumerate(
        zip(results["documents"][0], results["metadatas"][0])
    ):
        print(f"  Result {i + 1}:")
        print(f"    Source:   {meta['source']}")
        print(f"    Category: {meta['category']}")
        print(f"    Preview:  {doc[:120]}...")
        print()

    for meta in results["metadatas"][0]:
        assert meta["category"] == "brand", (
            f"Expected category='brand', got '{meta['category']}'"
        )
    print("  PASSED — all results are from category 'brand'\n")


def test_ops_vendor_query():
    """
    Ask about vendor decisions.
    Expect: vendor_decisions.txt should be the top result.
    """
    print("=" * 60)
    print("TEST 5: Operations — vendor query")
    print("Query: What vendor was selected for Brand B's campaign?")
    print("=" * 60)

    embedder = Embedder()
    store = VectorStore(embedder)

    results = store.search(
        query="What vendor was selected for Brand B's campaign?",
        n_results=3,
        category="ops",
    )

    print()
    for i, (doc, meta) in enumerate(
        zip(results["documents"][0], results["metadatas"][0])
    ):
        print(f"  Result {i + 1}:")
        print(f"    Source:   {meta['source']}")
        print(f"    Category: {meta['category']}")
        print(f"    Preview:  {doc[:120]}...")
        print()

    top_source = results["metadatas"][0][0]["source"]
    assert top_source == "vendor_decisions.txt", (
        f"Expected vendor_decisions.txt, got {top_source}"
    )
    print("  PASSED — top result is vendor_decisions.txt\n")


if __name__ == "__main__":
    print()
    print("[TEST] THINK9 BRAIN - PHASE 4 RETRIEVAL TESTS")
    print()

    test_legal_query()
    test_brand_a_query()
    test_category_filter_legal()
    test_category_filter_brand()
    test_ops_vendor_query()

    print("=" * 60)
    print("ALL 5 TESTS PASSED!")
    print("=" * 60)
