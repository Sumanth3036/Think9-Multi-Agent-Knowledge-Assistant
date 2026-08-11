from app.agents.confidence_gate import ConfidenceGate, CONFIDENCE_THRESHOLD


def test_gate(description, confidence, categories, expected):
    gate = ConfidenceGate()

    result = gate.evaluate(
        confidence=confidence,
        categories=categories,
    )

    status = result["status"]
    passed = status == expected

    print("\n" + "=" * 60)
    print(description)
    print(f"Confidence: {confidence}")
    print(f"Categories: {categories}")
    print(f"Expected:   {expected}")
    print(f"Actual:     {status}")
    print("PASSED" if passed else "FAILED")

    assert passed, (
        f"{description}: expected {expected}, got {status}"
    )


def main():
    print("\n" + "=" * 60)
    print("THINK9 BRAIN - PHASE 10 CONFIDENCE GATE TESTS")
    print(f"Threshold: {CONFIDENCE_THRESHOLD}")
    print("=" * 60)

    test_gate(
        "TEST 1 — High-confidence brand",
        91,
        ["brand"],
        "approved",
    )

    test_gate(
        "TEST 2 — Low-confidence brand",
        65,
        ["brand"],
        "pending_review",
    )

    test_gate(
        "TEST 3 — High-confidence legal",
        95,
        ["legal"],
        "pending_review",
    )

    test_gate(
        "TEST 4 — Multi-category legal",
        92,
        ["legal", "brand"],
        "pending_review",
    )

    test_gate(
        "TEST 5 — Exactly threshold",
        80,
        ["brand"],
        "approved",
    )

    print("\n" + "=" * 60)
    print("ALL 5 CONFIDENCE GATE TESTS PASSED")
    print("=" * 60)


if __name__ == "__main__":
    main()