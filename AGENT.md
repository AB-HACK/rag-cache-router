# Agent Instructions: Semantic Caching & Cost-Aware Routing for RAG

You are an expert Python / ML-systems engineer working on a two-person portfolio project: a **RAG service that cuts LLM cost and latency** using a semantic cache and a cost-aware model router, and **proves the savings with a repeatable evaluation**.

Place this file at the repo root as `AGENT.md` (or copy it into your AI tool's rules folder). The full spec lives in the PRD; this file tells you how to build it. If this file and the PRD disagree, stop and ask.

---

## 1. Project Summary

A plain RAG service (the **baseline**) is upgraded with:

- **Semantic cache:** returns a saved answer when a new question means the same as an old one, the similarity is at or above a tuned threshold, and the documents have not changed (`corpus_version`).
- **Cost-aware router:** labels each cache-miss question `simple` or `complex`. Simple goes to a small, cheap model; complex goes to a large model.
- **Escalation:** if the small model's answer looks weak, redo the question on the large model.
- **Request log + dashboard:** every request is logged; a Streamlit dashboard shows cost, hit rate, route split, p50/p95 latency and quality.
- **Comparison run:** baseline vs new system on the eval set **plus reworded (repeat) traffic**, producing the numbers for the README and resume line.

**The product is the evidence.** A feature without a measurement is unfinished.

**Resume target:** "Added semantic caching and cost-aware model routing to a RAG service, cutting LLM cost by X% and p95 latency by Y% with no drop in answer quality on a Z-question eval set." X, Y, Z must come from recorded runs, never from guesses.

### Team and phases

| Phase | Owner | Scope |
| --- | --- | --- |
| 0: Baseline | Abdul | Corpus, RAG pipeline, API, eval set, scoring script, logging, `baseline-v1` |
| Catch-up | Samad | Reads the PRD, reviews baseline PRs |
| 1A: Cache | Samad (suggested) | Cache, `corpus_version`, TTL, threshold tuning |
| 1B: Router | Abdul (suggested) | Router, labelled queries, escalation |
| 2: Finish | Split | Dashboard, comparison run, README |

Do not start Phase 1 work until `baseline-v1` is tagged.

---

## 2. Tech Stack (locked)

| Layer | Choice |
| --- | --- |
| Language | Python 3.11+ |
| API | FastAPI (async) |
| Vector store (corpus and cache) | Qdrant (Redis vector search is the allowed alternative; decide once, then stay consistent) |
| Embeddings | sentence-transformers (one model, shared by corpus and cache) |
| Model calls | LiteLLM (one interface for small and large models) |
| Request logs | SQLite for dev; Postgres optional later |
| Dashboard | Streamlit |
| Tests | pytest |
| Packaging | Docker + docker compose |
| Lint / format | Ruff + Black, with pre-commit |

Do not add libraries, frameworks or services outside this list without asking. No LangChain-style orchestration frameworks: the pipeline is small and should stay readable and testable.

---

## 3. Core Principles

- **DRY, SOLID, KISS, YAGNI, SoC, pragmatic TDD.**
- **Baseline first, always.** No change ships without being comparable to `baseline-v1`.
- **Measure, then claim.** Numbers come from scripts and saved CSVs.
- **Correctness before savings.** A wrong cached answer is worse than no cache.
- **Config over code.** Thresholds, TTLs, model names, prices and top-k live in config files.
- **Reproducible.** Fixed eval files, fixed seeds, tagged commits, recorded model names.
- **Readable by both teammates.** Either person must be able to explain every module in an interview.

---

## 4. Repository Structure (mandatory)

```
rag-cache-router/
  README.md
  AGENT.md
  docker-compose.yml
  .env.example
  .gitignore
  pyproject.toml
  config/
    models.yaml            # model names, price per 1K input/output tokens
    settings.yaml          # threshold, TTL, top-k, chunk size, corpus_version
  data/
    corpus/                # source documents + SOURCES.md (origin, licence)
  eval/
    eval_set.jsonl
    paraphrase_pairs.csv
    near_miss_pairs.csv
    router_labels.csv
    paraphrased_traffic.jsonl
  src/
    api/                   # FastAPI app, routes, schemas, dependencies
    rag/                   # chunking, embedding, retrieval, generation
    cache/                 # semantic cache (lookup, store, versioning, TTL)
    router/                # classifier, escalation checks
    logging/               # request logger (SQLite)
    dashboard/             # Streamlit app
    core/                  # settings loader, cost calculator, shared types
  scripts/
    ingest.py              # build the corpus index
    run_eval.py            # scoring script
    tune_threshold.py      # threshold sweep
    compare.py             # baseline vs new system
  results/                 # small CSVs from runs, committed
  tests/
  docs/
```

Rules:

- Routes are thin: validate input, call a service function, return the response.
- Business logic lives in `src/rag`, `src/cache`, `src/router`, `src/core`.
- Scripts import the **same** functions the API uses. Never duplicate pipeline logic in a script.
- Always keep `.env.example` (placeholders only) and a correct `.gitignore`.

---

## 5. Request Flow (single source of truth)

```python
def answer(query: str, tenant_id: str | None = None) -> dict:
    q_vec = embed(normalize(query))
    hit = cache.nearest(q_vec, tenant_id=tenant_id)
    if hit and hit.score >= THRESHOLD and hit.version == CORPUS_VERSION:
        log_request(query, cache_hit=True)
        return hit.payload

    route = classify(query)  # "simple" or "complex"
    model = SMALL_MODEL if route == "simple" else LARGE_MODEL
    result = rag_pipeline(query, model=model)
    if route == "simple" and needs_escalation(result):
        result = rag_pipeline(query, model=LARGE_MODEL)

    if is_cacheable(result):  # never cache errors, empty, "I don't know", or personalized answers
        cache.store(q_vec, result, version=CORPUS_VERSION, tenant_id=tenant_id)
    log_request(query, cache_hit=False, route=route, result=result)
    return result
```

Do not change this order without updating the PRD. The cache is checked before the router; escalation happens before the cache write; every path logs.

---

## 6. Domain Rules (non-negotiable)

### Semantic cache

- Normalize (lowercase, strip punctuation and extra whitespace) before embedding.
- Use the **same embedding model** for the corpus, the cache and queries.
- A hit requires **both** similarity at or above the threshold **and** a matching `corpus_version`.
- Every entry stores: query embedding, query text, answer, sources, timestamp, TTL, `corpus_version`, optional `tenant_id`.
- Bump `corpus_version` whenever documents are re-ingested. Add a TTL as a second safety net.
- **Never cache:** errors, empty answers, "I don't know" answers, or answers that depend on who is asking (unless the key includes `tenant_id` / `user_id`).
- Cache storage is separate from the document collection.
- Target: cache hits answer in under 100 ms.

### Threshold tuning

- Tune on about **50 paraphrase pairs** (must hit) and about **50 near-miss pairs** (must not hit). Example near-miss: "refund policy in the EU" vs "refund policy in the US".
- Sweep 0.85 to 0.97. Choose the **lowest value with zero false hits** on the near-miss set.
- Record the chosen value and test-set sizes in the README.
- If no value gives zero false hits, raise the range or rewrite ambiguous pairs. Never accept false hits to improve the hit rate.

### Router and escalation

- Start with a **transparent rule-based** router. Signals: query length, number of entities or concepts, complexity words (compare, why, explain, difference, versus), retrieval-score spread.
- Log which signals fired for every decision.
- Validate on about 100 hand-labelled queries. A complex question routed as simple hurts quality; the reverse only wastes money, so tune to avoid the first.
- Escalate when retrieval scores are low, citations are missing, or the answer says "I don't know".
- **Escalated requests cost both calls.** Count tokens and cost for both, or the savings are overstated.
- A tiny LLM classifier is optional and must be compared on accuracy **and** its own cost.

### Cost and latency

- Cost = (input tokens × input price) + (output tokens × output price), from `config/models.yaml`. Never hard-code prices.
- Prices change; re-check provider rates before the final comparison run.
- Report p50 and p95 latency, with p95 as the headline number.

### Evaluation and comparison

- The **eval set** is the most valuable file in the repo. Every reference answer is hand-checked. Never edit it after a baseline run without tagging a new version.
- The comparison run must include the eval set **plus reworded versions** of it (repeat traffic). Testing only unique questions hides the cache's value.
- Quality must be about equal to the baseline on the same questions. If it drops, tune escalation or the threshold before claiming savings.
- Keep the AI-judge prompt fixed in the repo and spot-check a sample by hand.
- Save every run as a CSV in `results/` and tag the commit.

---

## 7. API and Performance Standards

### Async

- All I/O (vector store, model calls, database) uses `async`/`await`. Never block the event loop.
- CPU-bound work (embedding) must not stall request handling; run it in a thread pool or a dedicated worker if needed.

### Endpoints

- `POST /ask` returns: `answer`, `sources`, `route`, `cache_hit`, `model_used`, `escalated`, `cost_usd`, `latency_ms`.
- `GET /health` for liveness.
- Version URLs if more endpoints are added (`/api/v1/...`).
- Any list endpoint must paginate:

```json
{ "items": [], "total": 125, "page": 1, "size": 20, "pages": 7 }
```

### Errors

Use one consistent error shape and proper status codes:

```json
{ "detail": "Human readable message", "code": "MACHINE_READABLE_CODE" }
```

A failed model call returns a clear error, is logged with the `error` field, and is **never cached**.

### Other

- Enable GZip on responses.
- Create connection pools and clients once at startup, never per request.
- Retry model calls with backoff and save partial eval results so a long run can resume after a rate limit.
- Use dependency injection for settings, the vector client and the logger.
- Keep OpenAPI docs accurate (Pydantic models drive them).

---

## 8. Data and Logging Contract

Both teammates write to the same log. Do not change the schema without agreeing together and updating the PRD.

Table `requests`:

`id`, `timestamp`, `query`, `tenant_id` (optional), `cache_hit`, `cache_score` (optional), `route` (`simple` / `complex` / `cache`), `router_signals` (JSON), `model_used`, `escalated`, `input_tokens`, `output_tokens`, `cost_usd`, `latency_ms`, `quality_score` (optional), `corpus_version`, `error` (optional).

Rules:

- Every request is logged, hit or miss, success or failure.
- Tokens and cost include any escalation call.
- Do not log secrets or API keys. Avoid logging personal data; if real user data is ever used, minimize it and set short TTLs.

---

## 9. Security Guidelines

- Secrets only in environment variables. `.env` is git-ignored; commit `.env.example` with placeholders.
- If a key is ever pushed, revoke it immediately. Deleting the commit is not enough.
- Validate all input with Pydantic (length limits on queries).
- Treat retrieved documents and user queries as untrusted text. Do not let document content change system behavior, tool use or config. Keep the system prompt separate from retrieved text.
- Isolation: if answers can depend on the asker, include `tenant_id` or `user_id` in the cache key and lookup filter. Add a two-user test.
- Do not commit data you are not allowed to share. Note the corpus source and licence in `data/corpus/SOURCES.md`.
- Restrict CORS outside local development.

---

## 10. Testing Requirements

Write tests (pytest) for:

| Area | Must test |
| --- | --- |
| Cache | Paraphrase pair hits; near-miss pair does not; bumping `corpus_version` forces a miss; expired entries are not served; errors and empty answers are never stored; two tenants never see each other's entries |
| Threshold | The chosen threshold gives zero false hits on `near_miss_pairs.csv` |
| Router | Obvious simple and complex queries route correctly; signals are logged |
| Escalation | A weak small-model answer is redone on the large model; both costs are counted |
| Cost | Cost calculation matches the price table for known token counts |
| Logging | Every request produces exactly one log row, including failures |
| API | `/ask` happy path and error path; `/health` |

Rules:

- Mock model calls in unit tests so they are fast and free. Real model calls belong in eval scripts only.
- Fix random seeds. Tests must not depend on network access or wall-clock time.
- Aim for confidence in the critical paths, not 100% coverage.

---

## 11. Code Style and Naming

**Python**

- `snake_case` for functions, variables, modules; `PascalCase` for classes and Pydantic models; `UPPER_SNAKE_CASE` for constants.
- Full type hints on all functions.
- Boolean names start with `is_`, `has_`, `can_` (log columns such as `cache_hit` and `escalated` follow the schema).
- Every public function or class in `src/` has a docstring covering purpose and key parameters.
- Comment the *why* of non-obvious rules: threshold choice, escalation checks, version invalidation.
- No magic numbers: thresholds, TTLs, top-k, chunk size and prices come from config.

---

## 12. Git and Collaboration

- One repo; `main` is protected. All changes go through pull requests.
- One branch per task, named `feat/...`, `fix/...` or `docs/...` (for example `feat/semantic-cache`, `feat/router`).
- Each teammate reviews the other's PRs so both understand the whole system.
- Reference the task ID from the task division (for example `1A.4`) in the PR title.
- Commit messages: short imperative summary, for example `Add corpus_version check to cache lookup`.
- Tag milestones: `baseline-v1` (M0), M1 (cache and router pass tests), M2 (merged system), M3 (comparison and README done).
- Commit: code, configs, eval and pair files, small result CSVs, README, diagram, `docker-compose.yml`.
- Never commit: API keys, large datasets or model files, vector DB data folders, SQLite log files.

---

## 13. When Writing or Changing Code

Always:

1. Check whether the change touches the **critical path**: baseline run, cache hit path, near-miss threshold test, escalation, comparison run. Protect it.
2. Keep route handlers thin and logic in services.
3. Prefer async for I/O.
4. Add or update tests for business logic.
5. Re-run the scoring script after any change to retrieval, prompts, thresholds or routing, and compare with `baseline-v1`.
6. Update the README and PRD when behavior or setup changes.
7. Explain your reasoning briefly in the PR description.

Never:

- Put business logic in route handlers.
- Hard-code secrets, prices, model names or thresholds.
- Cache errors, empty answers or personalized answers without isolation.
- Lower the threshold to raise the hit rate if it creates false hits.
- Change the eval set, paraphrase pairs or near-miss pairs to make a result look better.
- Report a metric that was not produced by a saved script run.
- Implement out-of-scope features (see below).

---

## 14. Out of Scope (YAGNI)

Do not build these in the first version. Mention them as future work in the README if relevant.

- Full multi-tenant isolation beyond a simple `tenant_id` key
- Automatic threshold re-tuning in production
- A/B testing infrastructure or online learning of the router
- Changes to the underlying retrieval design
- User accounts, authentication, cloud deployment

---

## 15. Definition of Done

A task is done when:

- Code is merged through a reviewed PR.
- Tests for the changed behavior pass.
- The scoring script has been re-run and results are saved when quality, cost or latency could be affected.
- The README or PRD reflects any change in behavior.
- No secrets or data files were committed.

The project is done when all acceptance criteria in PRD Section 16 are ticked: baseline tagged, cache live and versioned, threshold tuned with zero false hits, router validated, escalation tested, dashboard working, comparison recorded, README with measured numbers and a dashboard screenshot.

---

## 16. Starting Prompt for Scaffolding

When asked to scaffold the project, do exactly this, then stop and wait for the next instruction:

1. Create the folder structure in Section 4.
2. Set up `pyproject.toml` with the stack in Section 2, plus Ruff, Black, pytest and pre-commit.
3. Create `config/settings.yaml` (threshold, TTL, top-k, chunk size, `corpus_version`) and `config/models.yaml` (small and large model names, prices) with placeholder values clearly marked.
4. Create `.env.example`, `.gitignore`, `docker-compose.yml` (Qdrant, optionally Redis) and a README with setup steps.
5. Create a FastAPI app with a settings loader, shared clients created at startup, GZip middleware, a consistent error handler, and `GET /health`.
6. Add placeholder modules with docstrings and TODOs for: `rag/` (chunk, embed, retrieve, generate), `cache/`, `router/`, `logging/` (with the `requests` table from Section 8), and `core/` (settings, cost calculator).
7. Add empty script stubs: `ingest.py`, `run_eval.py`, `tune_threshold.py`, `compare.py`.
8. Add one passing test (for example, health check and cost calculator).

Do not implement the cache, router or dashboard during scaffolding.

---

**When in doubt:** choose the simpler, more measurable, more correct option. If a decision affects the log schema, the eval set, the threshold or the request flow, ask first.
