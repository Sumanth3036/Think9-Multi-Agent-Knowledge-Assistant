from app.agents.legal_agent import LegalAgent
from app.agents.brand_agent import BrandAgent
from app.agents.operations_agent import OperationsAgent


def print_results(name, results):
    print("\n" + "=" * 60)
    print(name)
    print("=" * 60)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    for i, (document, metadata) in enumerate(
        zip(documents, metadatas), start=1
    ):
        print(f"\nResult {i}")
        print(f"Source: {metadata['source']}")
        print(f"Category: {metadata['category']}")
        print(f"Text: {document[:200]}...")


def main():
    legal_agent = LegalAgent()
    brand_agent = BrandAgent()
    operations_agent = OperationsAgent()

    legal_results = legal_agent.search(
        "Can we run a two-for-one promotion?"
    )

    brand_results = brand_agent.search(
        "What happened with Brand A's promotion?"
    )

    operations_results = operations_agent.search(
        "Which vendor was selected for Brand B?"
    )

    print_results("LEGAL AGENT", legal_results)
    print_results("BRAND AGENT", brand_results)
    print_results("OPERATIONS AGENT", operations_results)


if __name__ == "__main__":
    main()
