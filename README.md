# CompanyGPT — Internal RAG Chatbot

An internal AI chatbot for AtliQ company built with RAG (Retrieval Augmented Generation), Role Based Access Control (RBAC), guardrails, and evaluation. Entirely free to run.

---

## What it does

- Answers questions using company's private documents
- Restricts data access based on user role (HR, Finance, Marketing, Engineering, C-Level)
- Detects and masks PII using Microsoft Presidio
- Blocks out-of-scope questions
- Tracks token usage
- Evaluates answer quality using RAGAS

---

## Tech stack

| Layer | Tool |
|---|---|
| LLM | Llama 3.1 8B via Groq (free) |
| Embeddings | sentence-transformers all-MiniLM-L6-v2 (local) |
| Vector DB | Qdrant (local disk) |
| Reranking | FlashRank (local) |
| Orchestration | LangChain |
| PII detection | Microsoft Presidio |
| Auth | PyJWT + SQLite |
| Frontend | Streamlit |
| Evaluation | RAGAS |
| Tracing | LangSmith |

---

## Project structure
```
atliq_rag/
├── data/raw/               # company documents by department
│   ├── hr/
│   ├── finance/
│   ├── marketing/
│   ├── engineering/
│   └── general/
├── ingestion/              # document loading, chunking, embedding
├── retrieval/              # Qdrant vector store + reranker
├── auth/                   # JWT auth + RBAC + SQLite users
├── guardrails/             # PII detection + scope checker
├── rag/                    # LangChain RAG chain + LLM client
├── monitoring/             # token usage tracking + LangSmith
├── evaluation/             # RAGAS evaluation pipeline
├── frontend/               # Streamlit app
├── database/               # SQLite init + schema
└── docker/                 # Qdrant Docker compose
```

---

## Roles and data access

| Role | Access |
|---|---|
| HR | HR data, General |
| Finance | Finance reports, General |
| Marketing | Marketing reports, General |
| Engineering | Engineering docs, General |
| C-Level | All departments |

---

## Quick start

### 1. Clone the repo
```bash
git clone https://github.com/yourusername/companygpt.git
cd companygpt
```

### 2. Create virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

### 4. Set up environment variables
```bash
cp .env.example .env
# edit .env and add your GROQ_API_KEY and LANGCHAIN_API_KEY
```

### 5. Initialize database
```bash
python database/init_db.py
```

### 6. Run ingestion (one time only)
```bash
python -m ingestion.ingest_pipeline
```

### 7. Run the app
```bash
streamlit run frontend/app.py
```

---

## Demo accounts

| Username | Password | Role |
|---|---|---|
| alice | alice123 | HR |
| bob | bob123 | Finance |
| carol | carol123 | Marketing |
| dave | dave123 | Engineering |
| eve | eve123 | C-Level |

---

## Running evaluations
```bash
python -m evaluation.run_evals
```
Results saved to `evaluation/eval_results.csv`

---

## Notes

- Qdrant runs on local disk — embeddings persist across restarts in `qdrant_storage/`
- Ingestion only needs to run once unless you add new documents
- All components are free — no paid APIs required
- RAGAS scores may appear low due to Llama 8B limitations — actual answer quality is good as verified by manual testing