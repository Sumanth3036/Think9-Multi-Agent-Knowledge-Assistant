from app.agents.legal_agent import LegalAgent
from app.agents.synthesizer import AnswerSynthesizer


def main():
    query = "What are the rules for two-for-one promotions?"

    legal_agent = LegalAgent()

    results = legal_agent.search(
        query=query,
        n_results=4,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    evidence = []

    for document, metadata in zip(documents, metadatas):
        evidence.append(
            {
                "text": document,
                "source": metadata["source"],
                "category": metadata["category"],
            }
        )

    synthesizer = AnswerSynthesizer()

    answer = synthesizer.synthesize(
        query=query,
        evidence=evidence,
    )

    print("\n" + "=" * 60)
    print("THINK9 BRAIN — ANSWER SYNTHESIS")
    print("=" * 60)

    print("\nQuestion:")
    print(query)

    print("\nAnswer:")
    print(answer)

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
