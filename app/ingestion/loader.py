from pathlib import Path


DATA_DIR = Path("data")


def load_documents():
    documents = []

    for file_path in DATA_DIR.rglob("*.txt"):
        category = file_path.parent.name

        text = file_path.read_text(encoding="utf-8")

        documents.append(
            {
                "text": text,
                "source": file_path.name,
                "category": category,
            }
        )

    return documents
