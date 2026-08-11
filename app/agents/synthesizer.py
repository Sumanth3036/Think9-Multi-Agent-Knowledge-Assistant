import requests


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"


class AnswerSynthesizer:
    def __init__(self):
        self.url = OLLAMA_URL
        self.model = MODEL_NAME

    def synthesize(self, query, evidence):
        prompt = self._build_prompt(query, evidence)

        response = requests.post(
            self.url,
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        return data["response"].strip()

    def _build_prompt(self, query, evidence):
        evidence_text = []

        for item in evidence:
            evidence_text.append(
                f"""
SOURCE: {item['source']}
CATEGORY: {item['category']}
CONTENT:
{item['text']}
"""
            )

        combined_evidence = "\n".join(evidence_text)

        return f"""
You are Think9 Brain, an institutional knowledge assistant.

Answer the user's question using ONLY the provided evidence.

Do not use outside knowledge.
Do not invent facts.
If the evidence is insufficient, clearly say that there is not enough
information to answer confidently.

Always mention the source documents used.

USER QUESTION:
{query}

EVIDENCE:
{combined_evidence}

Provide a concise, factual answer.

At the end, include:

Sources:
- <source document>
- <source document>
"""
