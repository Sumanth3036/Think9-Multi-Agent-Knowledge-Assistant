from app.ingestion.loader import load_documents
from app.ingestion.chunker import chunk_text
from app.ingestion.embedder import Embedder
from app.retrieval.vector_store import VectorStore


def main():
    documents = load_documents()

    print(f"Loaded {len(documents)} documents")

    chunked_documents = []

    for document in documents:
        chunks = chunk_text(document["text"])

        for chunk in chunks:
            chunked_documents.append(
                {
                    "text": chunk,
                    "source": document["source"],
                    "category": document["category"],
                }
            )

    print(f"Created {len(chunked_documents)} chunks")

    embedder = Embedder()

    vector_store = VectorStore(embedder)

    vector_store.add_documents(chunked_documents)

    print("Documents successfully stored in ChromaDB")


if __name__ == "__main__":
    main()
