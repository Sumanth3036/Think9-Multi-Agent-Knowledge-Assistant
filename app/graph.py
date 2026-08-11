"""Phase 11 application workflow.

This module deliberately coordinates the existing Phase 1--10 components;
it does not replace their routing, retrieval, synthesis, or memory logic.
"""

from typing import Dict, List

class Think9Graph:
    def __init__(self):
        # Importing the specialist modules initializes the local embedding
        # runtime. Keep that cost on verification requests, not health/docs.
        from app.agents.brand_agent import BrandAgent
        from app.agents.confidence_gate import ConfidenceGate
        from app.agents.legal_agent import LegalAgent
        from app.agents.operations_agent import OperationsAgent
        from app.agents.orchestrator import Orchestrator
        from app.agents.synthesizer import AnswerSynthesizer

        self.orchestrator = Orchestrator()
        self.agents = {
            "legal": LegalAgent(),
            "brand": BrandAgent(),
            "ops": OperationsAgent(),
        }
        self.synthesizer = AnswerSynthesizer()
        self.confidence_gate = ConfidenceGate()

    @staticmethod
    def _evidence_from_results(results: Dict) -> List[Dict[str, str]]:
        documents = (results.get("documents") or [[]])[0] or []
        metadatas = (results.get("metadatas") or [[]])[0] or []
        evidence = []
        seen = set()
        for document, metadata in zip(documents, metadatas):
            source = metadata.get("source", "unknown")
            key = (source, document)
            if key not in seen:
                evidence.append({
                    "text": document,
                    "source": source,
                    "category": metadata.get("category", "unknown"),
                })
                seen.add(key)
        return evidence

    @staticmethod
    def _confidence(evidence: List[Dict[str, str]]) -> int:
        """A transparent integration score until a dedicated scorer is supplied."""
        if not evidence:
            return 0
        return min(95, 80 + len({item["source"] for item in evidence}) * 5)

    def run(self, question: str, db) -> Dict:
        from app.memory.decision_log import (
            create_decision,
            store_decision_in_vector_memory,
        )

        categories = self.orchestrator.route(question)
        evidence = []
        for category in categories:
            evidence.extend(self._evidence_from_results(
                self.agents[category].search(question)
            ))

        sources = list(dict.fromkeys(item["source"] for item in evidence))
        confidence = self._confidence(evidence)
        if not evidence:
            answer = "There is not enough evidence in Think9 Brain to answer confidently."
            status = "rejected"
        else:
            answer = self.synthesizer.synthesize(question, evidence)
            status = self.confidence_gate.evaluate(confidence, categories)["status"]

        decision = create_decision(
            db=db,
            question=question,
            answer=answer,
            confidence=confidence,
            categories=",".join(categories),
            sources=",".join(sources),
            status=status,
        )
        if status == "approved":
            store_decision_in_vector_memory(decision)

        return {
            "question": question,
            "answer": answer,
            "confidence": confidence,
            "categories": categories,
            "sources": sources,
            "status": status,
            "review_required": status == "pending_review",
            "decision_id": decision.id,
        }


def run_workflow(question: str, db) -> Dict:
    return Think9Graph().run(question, db)
