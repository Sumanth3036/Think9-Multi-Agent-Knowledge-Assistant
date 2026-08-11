# Think9 Brain

**A multi-agent institutional knowledge assistant** that retrieves information from legal, brand, and operations documents, generates grounded answers using a local Llama model, applies a confidence gate and human review workflow, and stores approved decisions as reusable organizational memory.

---

## The Problem

Organizational knowledge is scattered across departments — legal playbooks, brand histories, operations notes, vendor decisions, and prior rulings. An employee with a question often doesn't know which document or department holds the answer.

For example:

> "What are the rules for two-for-one promotions?"

Rather than manually searching through legal documents, Think9 Brain automates the path from question to answer:

```
Question
   ↓
Find relevant specialist
   ↓
Find relevant company knowledge
   ↓
Generate answer
   ↓
Check confidence
   ↓
Human review if required
   ↓
Store approved decision
```

Think9 Brain isn't just a chatbot — it also builds **institutional memory**, so future questions can be answered from prior approved decisions, not just raw documents.

---

## Architecture Overview

```
Streamlit (frontend)
    ↓
FastAPI (backend)
    ↓
Think9 Brain workflow
    ↓
Orchestrator → Specialist Agents (Legal / Brand / Operations)
    ↓
Retrieval (ChromaDB + Sentence Transformers)
    ↓
Synthesis (Llama 3.1 8B via Ollama)
    ↓
Confidence Gate
    ↓
Human Review (if required)
    ↓
Decision Memory (SQLite + ChromaDB)
```

### Frontend
**Streamlit** (`frontend/app.py`) — the interface where a user submits a question and interacts with the review workflow.

### Backend
**FastAPI** (`app/main.py`) — exposes the application's functionality through API endpoints, including `GET /` and `GET /docs`, along with verification and review endpoints.

### Orchestrator
`app/agents/orchestrator.py` decides which specialist(s) should handle a given question, using **deterministic keyword-based routing** across three specialists: **Legal**, **Brand**, and **Operations**. Multi-specialist routing is supported — a question spanning legal and brand topics can be routed to `["legal", "brand"]` simultaneously.

*(Note: this is keyword-based routing, not an LLM-based router. Semantic/LLM routing is listed as a future improvement below.)*

### Specialist Agents
- **Legal Agent** (`app/agents/legal_agent.py`) — draws on `data/legal/legal_playbook.txt`
- **Brand Agent** (`app/agents/brand_agent.py`) — draws on `data/brand/` (e.g. `brand_a_history.txt`, `brand_b_history.txt`, `brand_c_history.txt`)
- **Operations Agent** (`app/agents/operations_agent.py`) — draws on `data/ops/` (e.g. `vendor_decisions.txt`, `operations_notes.txt`, `meeting_notes_01.txt`, `meeting_notes_02.txt`)

---

## Knowledge Ingestion

`app/ingestion/` (`loader.py`, `chunker.py`, `embedder.py`, `run_ingestion.py`) turns raw documents into a searchable representation:

```
Documents → Load → Chunk → Create embeddings → Store in ChromaDB
```

The LLM never sees entire raw documents — only relevant, retrieved chunks.

### Embeddings
Uses **Sentence Transformers** with the **all-MiniLM-L6-v2** model to convert text into vectors, enabling semantic search (matching on meaning rather than exact keywords). The embedding model is loaded locally from cache for offline use.

---

## Retrieval

`app/retrieval/vector_store.py` manages two distinct memory stores in **ChromaDB**:

| Store | Contents |
|---|---|
| `think9_memory` | Original organizational documents (legal playbooks, brand histories, vendor decisions) |
| `think9_decisions` | Approved decisions from prior interactions |

> **Knowledge memory contains source material, while decision memory contains approved conclusions from previous interactions.**

Retrieval supports **semantic search with category filtering** — e.g. a query for "two-for-one promotions" retrieves `legal_playbook.txt` as the top result, and results can be filtered by `category = legal`, `category = brand`, or `category = ops`.

---

## Answer Synthesis (RAG)

`app/agents/synthesizer.py` uses **Ollama** running **Llama 3.1 8B** locally. The model is instructed to:

- Use only the provided evidence
- Not invent facts
- Not rely on outside knowledge
- Cite its sources

```
Retrieved evidence → Llama 3.1 → Grounded answer + Sources
```

This is a standard **retrieval-augmented generation (RAG)** pipeline.

### Example

**Question:** "What are the rules for two-for-one promotions?"

**Retrieval:** identifies `legal_playbook.txt` as relevant.

**Output:** Answer + Confidence (`85`) + Sources → status `pending_review`.

---

## Confidence Gate

`app/agents/confidence_gate.py` applies a threshold (currently **80**):

```
Confidence >= 80  →  Approved
Confidence < 80   →  Pending review
```

The confidence gate determines whether a generated decision can proceed automatically or requires human review.

---

## Human-in-the-Loop Review

```
pending_review
       ↓
   Human reviewer
    /        \
Approve      Reject
   ↓            ↓
approved    rejected
```

Every decision record carries a `status` field (`approved`, `pending_review`, or `rejected`). The system does not blindly trust the LLM:

> **AI proposes → confidence evaluates → human decides when necessary.**

---

## Decision Database

`app/memory/` (`database.py`, `models.py`, `decision_log.py`) — a **SQLite** database storing decision records, each containing:

- Question
- Answer
- Confidence
- Categories
- Sources
- Status
- Creation time

Example record:

```
Question:    Can Brand A run a two-for-one promotion?
Answer:      Brand A can use a two-for-one promotion when the
             promotional terms are clearly displayed.
Confidence:  91
Categories:  legal, brand
Status:      approved
```

---

## Decision Memory

Once approved, a decision is stored in `think9_decisions` in ChromaDB:

```
Original documents → Question → AI answer → Human approval → Decision memory
```

This allows semantically similar future questions to retrieve prior approved decisions. For example, a later query — "Can we use the same promotion structure?" — successfully retrieved the earlier approved decision about Brand A's two-for-one promotion.

### Why this matters

Without decision memory, every question restarts the same search-and-answer cycle. With Think9 Brain, approved answers are remembered and reused:

```
Employee asks question → Search documents → Answer
   → Human approval → Decision remembered → Future employees benefit
```

This is the core **institutional memory** concept behind the project.

---

## Integration (Phase 11)

Phase 11 wired the previously independent components — agents, retrieval, synthesis, memory, confidence gating, and review — into a single working application:

```
User → FastAPI → Workflow → Orchestrator → Agents → Retrieval
     → Synthesis → Confidence → Review → Decision Memory
```

Integration is covered by `tests/test_api.py` and `tests/test_phase11.py`.

---

## Project Structure

```
think9-brain/
│
├── app/
│   ├── agents/
│   │   ├── brand_agent.py
│   │   ├── legal_agent.py
│   │   ├── operations_agent.py
│   │   ├── orchestrator.py
│   │   ├── synthesizer.py
│   │   └── confidence_gate.py
│   │
│   ├── ingestion/
│   │   ├── loader.py
│   │   ├── chunker.py
│   │   ├── embedder.py
│   │   └── run_ingestion.py
│   │
│   ├── memory/
│   │   ├── database.py
│   │   ├── models.py
│   │   └── decision_log.py
│   │
│   ├── retrieval/
│   │   └── vector_store.py
│   │
│   ├── review/
│   │   └── confidence.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── graph.py
│   └── main.py
│
├── data/
│   ├── brand/
│   ├── legal/
│   └── ops/
│
├── frontend/
│   └── app.py
│
├── tests/
│
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit |
| API | FastAPI |
| Backend | Python |
| Agent orchestration | Custom workflow / graph |
| Specialist agents | Legal, Brand, Operations |
| Embeddings | Sentence Transformers |
| Embedding model | all-MiniLM-L6-v2 |
| Vector database | ChromaDB |
| LLM | Llama 3.1 8B |
| LLM runtime | Ollama |
| Decision database | SQLite |
| ORM | SQLAlchemy |
| Validation | Pydantic |

---

## Testing

Each major subsystem was tested independently — ingestion, retrieval, agents, orchestrator, synthesizer, confidence gate, memory, decision retrieval, and the review queue — and the integrated Phase 11 workflow (API + end-to-end flow) was also tested.

---

## Scope & Honest Claims

This project is a **working prototype demonstrating the proposed architecture**, not a production system. Specifically:

- The current orchestrator uses **deterministic keyword-based routing**, not an autonomous LLM-based router.
- The system **grounds generated answers in retrieved organizational evidence** and uses confidence gating plus human review — it does not guarantee factual correctness on its own.
- **Approved decisions are stored as reusable decision memory** — the system does not continuously learn or retrain.

---

## Limitations

1. **Routing** — current routing is deterministic/keyword-based rather than semantic.
2. **Local model dependency** — requires Ollama with `llama3.1:8b` available locally.
3. **Knowledge base** — the current dataset is a prototype/sample organizational knowledge base.
4. **Persistence** — SQLite and local ChromaDB suit a prototype but would need production infrastructure at scale.
5. **Human review** — functional but simpler than a production enterprise approval system.

---

## Future Improvements

- **Better routing** — replace keyword routing with semantic or LLM-based routing.
- **Better document ingestion** — support PDF, DOCX, emails, and meeting transcripts.
- **Authentication** — role-based permissions for employee, reviewer, and administrator.
- **Production databases** — move from local SQLite/ChromaDB to scalable infrastructure.
- **Monitoring** — track answer quality, retrieval quality, confidence, review rate, latency, and frequently asked questions.
- **Evaluation** — build a benchmark dataset of organizational questions with expected evidence/answers.

---

## The Story

```
COMPANY KNOWLEDGE
       │
       ▼
Legal / Brand / Operations Docs
       │
       ▼
    Vector Search
       │
       ▼
   Specialist Agent
       │
       ▼
    Llama 3.1 8B
       │
       ▼
  Grounded Answer
       │
       ▼
  Confidence Gate
      /       \
High confidence  Low confidence
     │               │
     ▼               ▼
 Approved        Human Review
     │               │
     └───────┬───────┘
             ▼
      Decision Memory
             │
             ▼
    Future Questions
```

Think9 Brain isn't simply an AI chatbot. It's a prototype that turns scattered organizational knowledge into a searchable knowledge system, uses specialized agents to answer questions from that knowledge, applies confidence-based human oversight, and converts approved decisions into reusable institutional memory.
