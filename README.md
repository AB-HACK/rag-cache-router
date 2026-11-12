# Semantic Caching & Cost-Aware Routing for RAG

A RAG service that reduces LLM cost and p95 latency using a versioned semantic cache and a cost-aware model router with escalation, verified by a repeatable evaluation harness.

## Results (Baseline vs. Upgraded System)

> *Populated after Phase 2 comparison runs (`scripts/compare.py`).*

| Metric | Baseline (Large Model, No Cache) | Upgraded (Cache + Router) | Change |
| --- | --- | --- | --- |
| Cost per request (USD) | TBD | TBD | TBD |
| p50 latency (ms) | TBD | TBD | TBD |
| p95 latency (ms) | TBD | TBD | TBD |
| Cache hit rate | 0% | TBD | TBD |
| Answer quality score | TBD | TBD | TBD |

## Setup

### 1. Prerequisites
- Python 3.11+
- Docker & Docker Compose

### 2. Environment Setup
```bash
# Copy environment template and add your API keys
cp .env.example .env

# Create virtual environment and install dependencies
python -m venv .venv
# On Windows: .venv\Scripts\activate
# On macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### 3. Start Vector Store
```bash
docker compose up -d
```

### 4. Run the API
```bash
uvicorn src.api.app:app --reload
```
Check liveness at `http://localhost:8000/health`.

### 5. Run Tests
```bash
pytest
```

## Evaluation & Threshold Tuning
- Ingest corpus: `python scripts/ingest.py`
- Run evaluation: `python scripts/run_eval.py`
- Tune cache threshold: `python scripts/tune_threshold.py`
- Run baseline vs. upgraded comparison: `python scripts/compare.py`
- Launch dashboard: `streamlit run src/dashboard/app.py`

## Limitations
*To be documented in Phase 2.*
