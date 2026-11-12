# Task Division: Semantic Caching & Cost-Aware Routing for RAG

Task IDs match Section 15 of the PRD.

**Team:** Samad and Abdul.

**Assumption:** "Phase one" means **Phase 0 (the baseline)**, the first phase. Abdul builds all of it while Samad studies the PRD. The cache, router and finish phases are then split between them. If the cache and router phase was meant instead, swap the owners in the tables below.

---

## Overview

| Phase | Owner | Goal |
| --- | --- | --- |
| 0: Baseline | **Abdul** (all of it) | Plain RAG service, eval set, scoring script, logging, baseline numbers |
| Catch-up (during Phase 0) | **Samad** | Read the PRD, review baseline pull requests, understand every part |
| 1A: Semantic cache | **Samad** (suggested) | Cache, versioning, TTL, threshold tuning |
| 1B: Router and escalation | **Abdul** (suggested) | Router, labelled queries, escalation |
| 2: Finish | Split | Dashboard, comparison run, README |

Phases 1A and 1B run in parallel on separate branches. Swap them if you prefer.

---

## Phase 0: Baseline (Abdul owns everything)

| ID | Task | Depends on | Rough time |
| --- | --- | --- | --- |
| 0.1 | Create GitHub repo, folder skeleton, `.gitignore`, `.env.example`; add Samad as collaborator | None | 1 h |
| 0.2 | Choose and add the corpus (50-200 documents) | 0.1 | 1-2 h |
| 0.3 | Chunking, embeddings, vector DB ingest | 0.2 | 2-3 h |
| 0.4 | Retrieval and answer generation with citations | 0.3 | 2-3 h |
| 0.5 | FastAPI `/ask` endpoint and `/health` | 0.4 | 1-2 h |
| 0.6 | Write and hand-check the eval set (50-100 questions) | 0.2 | 3-5 h |
| 0.7 | Scoring script and CSV output | 0.4, 0.6 | 2-3 h |
| 0.8 | Request logging using the agreed schema (PRD Section 11) | 0.5 | 1-2 h |
| 0.9 | Baseline run, save results, tag commit `baseline-v1` | 0.7, 0.8 | 1 h |

Times are rough guesses; revise them after Phase 0.

**Abdul's rules during Phase 0**

- Work on branches and open pull requests so Samad can review them.
- Write short comments or a `docs/baseline.md` explaining chunk size, embedding model, top-k and how scoring works.
- Tell Samad before changing the log schema. It is the contract for Phase 1.
- Post a short update when each task is merged.

---

## Samad's catch-up (during Phase 0)

| Step | What to do | Done when |
| --- | --- | --- |
| C1 | Read the whole PRD once, then re-read Sections 5, 6, 8 and 9 | Samad can explain the request flow without looking |
| C2 | Learn the glossary (Section 5): embedding, threshold, `corpus_version`, p50/p95, escalation | Samad can define each in one sentence |
| C3 | Review every Phase 0 pull request and ask at least one question per PR | Samad understands chunking, retrieval and scoring |
| C4 | Run the baseline locally from the README | The API answers a question on Samad's machine |
| C5 | Read the eval set and the baseline results CSV | Samad knows what "good" currently looks like |
| C6 | Optional prep that does not need the baseline: start drafting the 50 paraphrase pairs and 50 near-miss pairs (task 1A.3) | Draft files exist in `eval/` |

Gate: Samad does not start Phase 1 coding until C1-C5 are done and `baseline-v1` is tagged.

---

## Phase 1A: Semantic cache (Samad, suggested)

| ID | Task | Depends on | Rough time |
| --- | --- | --- | --- |
| 1A.1 | Semantic cache: normalize, embed, lookup, store | 0.9 | 2-3 h |
| 1A.2 | `corpus_version` and TTL | 1A.1 | 1 h |
| 1A.3 | Write 50 paraphrase pairs and 50 near-miss pairs | 0.9 | 2-3 h |
| 1A.4 | Threshold sweep (0.85 to 0.97); pick the lowest value with zero false hits | 1A.1, 1A.3 | 1-2 h |
| 1A.5 | Cache tests: paraphrase hits, near-miss does not, version bump, expiry, errors never stored | 1A.2 | 1 h |

Branch: `feat/semantic-cache`

---

## Phase 1B: Router and escalation (Abdul, suggested)

| ID | Task | Depends on | Rough time |
| --- | --- | --- | --- |
| 1B.1 | Model config through LiteLLM (small and large model, prices in config) | 0.9 | 1 h |
| 1B.2 | Rule-based router | 1B.1 | 2 h |
| 1B.3 | Hand-label 100 queries; measure router accuracy | 1B.2 | 2-3 h |
| 1B.4 | Escalation logic; count the cost of both calls | 1B.2 | 1-2 h |
| 1B.5 | Router and escalation tests | 1B.4 | 1 h |
| 1B.6 | Optional: tiny LLM classifier comparison | 1B.3 | 2 h |

Branch: `feat/router`

---

## Phase 2: Finish (split)

| ID | Task | Owner | Depends on | Rough time |
| --- | --- | --- | --- | --- |
| 2.1 | Merge cache and router into one request flow | Both (pair) | 1A.5, 1B.5 | 1-2 h |
| 2.2 | Streamlit dashboard (cost, hit rate, route split, p50/p95, quality) | **Samad** | 2.1 | 2-3 h |
| 2.3 | Build the reworded traffic set from the eval set | **Abdul** | 0.6 | 1-2 h |
| 2.4 | Comparison run: baseline vs new system; record cost %, p95 change, quality | **Abdul** | 2.1, 2.3 | 1-2 h |
| 2.5 | README: architecture diagram, results table, setup, Limitations | **Samad** (draft) | 2.2, 2.4 | 2-3 h |
| 2.6 | Review each other's work; fill in the resume line with real numbers | Both | 2.5 | 1 h |

---

## Working agreement

1. **One repo, protected `main`.** All changes go through pull requests.
2. **Review both ways.** Samad and Abdul review each other's PRs, so both understand the whole system for interviews.
3. **Log schema is shared.** Change it only after agreeing together.
4. **Tag milestones:**
   - M0: `baseline-v1` (baseline numbers saved)
   - M1: cache and router pass tests on their branches
   - M2: merged system answers end to end and logs everything
   - M3: comparison recorded and README complete
5. **Secrets stay in `.env`** (git-ignored). Never commit API keys.
6. **Track tasks** as GitHub Issues on a Projects board using the IDs above.
7. **Sync** briefly at each milestone: what is done, what is blocked, what changes.

## Open decisions (agree together)

- [ ] Confirm who owns Phase 1A and who owns Phase 1B
- [ ] Which corpus
- [ ] Small and large model, and the budget for eval runs
- [ ] Qdrant or Redis
- [ ] Target date for each milestone (M0-M3)
