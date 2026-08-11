import os

os.environ["USE_TF"] = "0"

from sentence_transformers import SentenceTransformer


class Embedder:
    def __init__(self):
        # The model is part of the local Think9 runtime.  Avoid remote metadata
        # checks on every specialist initialization: blocked/offline checks made
        # verification requests exceed the API and Streamlit timeouts.
        self.model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            local_files_only=True,
        )

    def embed(self, texts):
        return self.model.encode(
            texts,
            show_progress_bar=True
        ).tolist()
