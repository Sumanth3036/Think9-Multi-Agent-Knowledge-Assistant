
import chromadb


class VectorStore:
    def __init__(self, embedder):
        self.embedder = embedder

        self.client = chromadb.PersistentClient(
            path="chroma_db"
        )

        self.collection = self.client.get_or_create_collection(
            name="think9_memory"
        )

        self.decision_collection = self.client.get_or_create_collection(
            name="think9_decisions"
        )

    def add_documents(self, documents):
        texts = []
        metadatas = []
        ids = []

        for index, document in enumerate(documents):
            texts.append(document["text"])

            metadatas.append(
                {
                    "source": document["source"],
                    "category": document["category"],
                }
            )

            ids.append(f"doc_{index}")

        embeddings = self.embedder.embed(texts)

        self.collection.upsert(
            ids=ids,
            documents=texts,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def search(self, query, n_results=5, category=None):
        query_embedding = self.embedder.embed([query])[0]

        where = None

        if category:
            where = {
                "category": category
            }

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
        )

        return results

    def add_decision(self, decision_id, text, metadata):
        embedding = self.embedder.embed([text])[0]

        self.decision_collection.upsert(
            ids=[f"decision_{decision_id}"],
            documents=[text],
            metadatas=[metadata],
            embeddings=[embedding],
        )

    def search_decisions(self, query, n_results=3):
        query_embedding = self.embedder.embed([query])[0]

        results = self.decision_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
        )

        return results

