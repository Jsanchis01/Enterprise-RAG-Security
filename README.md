# Enterprise-RAG-Security

> **Design and Evaluation of a Policy-Aware Security and Governance Framework for Enterprise Retrieval-Augmented Generation (RAG) Systems**

---

## 1. Overview

Enterprise-RAG-Security is a modular monolith platform designed for enterprise-grade security, governance, and policy-aware retrieval in Retrieval-Augmented Generation (RAG) systems. The framework enables a rigorous, scientifically controlled comparison between **Baseline RAG** and **Policy-Aware RAG** across information access security, prompt injection defenses, knowledge poisoning mitigations, and audit completeness.

---

## 2. Architecture & Pipeline Design

The system is implemented as an explicit modular monolith without unnecessary orchestration frameworks or microservices.

```
Baseline RAG Flow:
Query ──► Dense Embedding ──► Unfiltered Vector Retrieval ──► Top-K Context ──► LLM Generation

Policy-Aware RAG Flow (Future Phases):
Query ──► Input Security Validation ──► Policy Filter Compilation ──► Filtered Retrieval ──► Context Security Validation ──► Top-K Authorized Context ──► LLM Generation
```

### Core Technology Stack
- **Backend**: Python 3.12.4, FastAPI 0.142.2, Pydantic V2 (2.13.5)
- **Database**: PostgreSQL 16.4 (Alpine), SQLAlchemy 2.0.35, Psycopg 3.2.3
- **Vector Engine**: Qdrant v1.19.1 (`qdrant-client==1.19.1`, Cosine distance)
- **Embeddings**: SentenceTransformers 6.1.0 (`all-MiniLM-L6-v2`, 384 dimensions)
- **Authentication & Security**: PyJWT 2.15.1 (JWT HS256), pwdlib 0.3.1 (Argon2id hashing)
- **Local Inference**: Native Host Ollama 0.35.1 (`qwen3:4b`)

---

## 3. Synthetic Enterprise Corpus (Phase 3)

The retrieval foundation utilizes a deterministic, reproducible synthetic corpus of **48 documents** across 4 corporate departments:

```
research/datasets/corpus/
├── manifest.json              # Complete JSON manifest of the 48 documents
└── data.py                    # Deterministic corpus generator with DNS UUIDv5 namespace
```

### Departmental Distribution & Clearance Levels
| Department | Total Docs | L1 (Public) | L2 (Internal) | L3 (Confidential) | L4 (Restricted) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Human Resources (HR)** | 12 | 2 | 4 | 4 | 2 |
| **Finance (FIN)** | 12 | 2 | 4 | 4 | 2 |
| **Engineering (ENG)** | 12 | 2 | 4 | 4 | 2 |
| **Legal (LEG)** | 12 | 2 | 4 | 4 | 2 |
| **Total** | **48** | **8** | **16** | **16** | **8** |

### Metadata Schema
Every document and chunk preserves 10 core metadata fields:
1. `document_id`: Deterministic UUID string
2. `title`: Descriptive document title
3. `department`: `hr`, `finance`, `engineering`, or `legal`
4. `classification`: `public`, `internal`, `confidential`, or `restricted`
5. `clearance_level`: Numeric level (`1` to `4`)
6. `source_type`: Origin category (e.g. `official_policy`, `technical_spec`, `executive_memo`)
7. `issuing_department`: Authorizing departmental entity
8. `author_role`: Functional role (e.g. `chief_financial_officer`, `principal_architect`)
9. `source_authority`: `authoritative`, `advisory`, or `standard`
10. `trust_status`: `certified` or `provisional`

---

## 4. Chunking, Embeddings & Vector Storage

### Deterministic Chunking
- Configurable chunk size (`chunk_size=400` chars) and overlap (`chunk_overlap=60` chars).
- Paragraph- and word-boundary aware.
- Deterministic chunk UUIDs: `uuid.uuid5(doc_id, f"chunk-{chunk_index:04d}")`.
- Canonical SHA-256 content hash: `hashlib.sha256(canonical_text).hexdigest()`.

### Vector Embeddings
- Model: `sentence-transformers/all-MiniLM-L6-v2`
- Dimensions: Dynamic (`384` dimensions)
- Metric: Cosine similarity

### Qdrant Collection
- Collection Name: `enterprise_knowledge_base`
- Vector Configuration: `size=384`, `distance=Cosine`
- Indexed Payload Fields: `department`, `classification`, `clearance_level`, `source_type`, `issuing_department`, `author_role`, `source_authority`, `trust_status`, `document_id`, `chunk_id`, `content_hash`, `text`.

---

## 5. Usage & Commands

### 1. Start Infrastructure Containers
```powershell
docker compose --env-file .env -f docker/docker-compose.yml up -d
```

### 2. Initialize Database & Seed Users (Phase 2)
```powershell
.\.venv\Scripts\python.exe scripts/init_db.py
.\.venv\Scripts\python.exe scripts/seed_users.py
```

### 3. Ingest & Index Document Corpus (Phase 3)
```powershell
.\.venv\Scripts\python.exe scripts/ingest_corpus.py
```

### 4. Execute Retrieval via Service
```python
from app.services.retrieval_service import get_retrieval_service

retrieval_service = get_retrieval_service()
results = retrieval_service.retrieve_chunks(
    query="What is the business travel meal allowance?",
    top_k=3
)

for rank, chunk in enumerate(results, start=1):
    print(f"[{rank}] Score: {chunk.similarity_score:.4f} | Title: {chunk.metadata['title']}")
    print(f"     Text: {chunk.text[:120]}...\n")
```

### 5. Run Test Suite
```powershell
.\.venv\Scripts\python.exe -m pytest backend/tests -v
```

---

## 6. Implementation Milestones

- [x] **Phase 1**: Repository foundation, pinned dependencies, Docker Compose (`postgres:16.4-alpine`, `qdrant:v1.19.1`), environment verification.
- [x] **Phase 2**: Relational schema, Argon2 password hashing (`pwdlib`), JWT authentication (`PyJWT`), RBAC & clearance tiers, user seeding, 13 automated tests.
- [x] **Phase 3**: 48-document synthetic corpus, deterministic chunking, SHA-256 chunk hashing, `all-MiniLM-L6-v2` embeddings, Qdrant indexing & retrieval service, 33 automated tests.
- [ ] **Phase 4**: Policy Engine & Policy-Aware Vector Retrieval (Clearance & Provenance Filtering).
- [ ] **Phase 5**: Input Security Validation, Context Security Validation & Host Ollama Integration.
- [ ] **Phase 6**: Hash-Chained Audit Logging & Security Telemetry.
- [ ] **Phase 7**: Automated Research Experiment Runner & Evaluation Metrics.
- [ ] **Phase 8**: React Enterprise Dashboard.
- [ ] **Phase 9**: Empirical Benchmarks & Documentation.
