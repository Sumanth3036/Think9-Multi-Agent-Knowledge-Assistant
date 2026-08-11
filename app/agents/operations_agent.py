from app.retrieval.vector_store import VectorStore
from app.ingestion.embedder import Embedder


class OperationsAgent:
    def __init__(self):
        self.embedder = Embedder()
        self.vector_store = VectorStore(self.embedder)

    def search(self, query, n_results=5):
        return self.vector_store.search(
            query=query,
            n_results=n_results,
            category="ops",
        )
