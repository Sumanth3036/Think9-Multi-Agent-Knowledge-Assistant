"""Logical Phase 11 integration test; external retrieval and Ollama are mocked."""

import sys
from types import ModuleType

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.graph import Think9Graph
from app.memory.database import Base
from app.memory.models import Decision


def main():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    db = sessionmaker(bind=engine)()
    graph = Think9Graph.__new__(Think9Graph)
    graph.orchestrator = type("Router", (), {"route": lambda _, __: ["brand"]})()
    graph.agents = {"brand": type("Agent", (), {"search": lambda _, __: {
        "documents": [["Brand evidence"]],
        "metadatas": [[{"source": "brand.txt", "category": "brand"}]],
    }})()}
    graph.synthesizer = type("Synth", (), {"synthesize": lambda _, q, e: "Evidence-backed answer."})()
    graph.confidence_gate = type("Gate", (), {"evaluate": lambda _, c, cats: {"status": "approved"}})()

    stored = []
    fake_log = ModuleType("app.memory.decision_log")

    def create_decision(**kwargs):
        kwargs.pop("db")
        decision = Decision(**kwargs)
        db.add(decision)
        db.commit()
        db.refresh(decision)
        return decision

    fake_log.create_decision = create_decision
    fake_log.store_decision_in_vector_memory = lambda decision: stored.append(decision.id)
    original_log = sys.modules.get("app.memory.decision_log")
    sys.modules["app.memory.decision_log"] = fake_log
    try:
        result = graph.run("What happened?", db)
    finally:
        if original_log is None:
            del sys.modules["app.memory.decision_log"]
        else:
            sys.modules["app.memory.decision_log"] = original_log

    assert result["status"] == "approved"
    assert result["sources"] == ["brand.txt"]
    assert result["decision_id"] in stored
    assert not db.query(Decision).filter(Decision.status == "pending_review").all()
    db.close()
    print("Phase 11 workflow integration PASSED")


if __name__ == "__main__":
    main()
