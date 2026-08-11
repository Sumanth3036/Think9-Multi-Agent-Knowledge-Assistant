from app.agents.orchestrator import Orchestrator


def test_route(query, expected):
    orchestrator = Orchestrator()

    result = orchestrator.route(query)

    print("\n" + "=" * 60)
    print(f"Query: {query}")
    print(f"Expected: {expected}")
    print(f"Actual: {result}")

    if result == expected:
        print("PASSED")
    else:
        print("FAILED")


def main():
    test_route(
        "What are the legal rules for two-for-one promotions?",
        ["legal"],
    )

    test_route(
        "What happened with Brand A's previous campaign?",
        ["brand"],
    )

    test_route(
        "Which vendor was selected for delivery?",
        ["ops"],
    )

    test_route(
        "What is the onboarding process?",
        ["ops"],
    )

    test_route(
        "Can Brand A run a promotion based on Brand B's previous experience?",
        ["legal", "brand"],
    )


if __name__ == "__main__":
    main()
