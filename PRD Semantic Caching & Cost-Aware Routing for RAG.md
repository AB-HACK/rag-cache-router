# PRD: Semantic Caching & Cost-Aware Routing for RAG

Oct 22, 2026 · @olasamad

## 1. Overview

This project upgrades a question-answering system (a RAG service) so it answers repeat questions from memory and sends easy questions to a cheaper AI model, cutting cost and waiting time without making answers worse.

**The help-desk analogy.** Picture a company help desk that answers staff questions from the company handbook. Today, every question, even one asked ten times this week, goes to the most expensive expert, who searches the handbook and writes a fresh answer. That is slow and costly.

The upgrade adds two things:

1. **A cache (memory).** If someone already asked the same thing in different words, hand back the saved answer. No expert is needed.
2. **A router (sorter).** If the question is new but easy, give it to a cheaper junior. Only hard questions reach the expensive expert. If the junior's answer looks weak, the expert redoes it.

**The problem.** Large AI models charge per word processed. In a real service many questions repeat or are simple, so always using the biggest model wastes money and adds delay.

**The proof.** The project is only worth showing if it comes with numbers. We first measure the plain system (the baseline), then the upgraded system, on the same test questions. The difference becomes the headline result for the README and the resume.

**What we deliver:**

- A working RAG service with semantic caching and cost-aware routing
- A test set and scoring script that make every result repeatable
- A dashboard showing cost, speed, cache hits and quality
- A GitHub repo with a README containing measured before/after numbers

## 2. Goals and success metrics

Success means lower cost and faster answers with no meaningful drop in quality, shown by numbers from a repeatable test run. Targets below are our starting proposals; we can adjust them after the baseline run shows what is realistic.

| Metric | Plain meaning | How it is computed | Target |
| --- | --- | --- | --- |
| Cost per request | Money spent on AI for one question | (input tokens × input price) + (output tokens × output price), from a price table in config | Lower than baseline; report the % cut |
| Cache hit rate | Share of questions answered from saved answers | cache hits ÷ total requests | As high as possible, with zero wrong hits |
| p50 latency | The typical wait for an answer | Median response time | Lower than baseline |
| p95 latency | The slow end: 95% of answers arrive faster than this | 95th percentile response time | Lower than baseline (most important latency number) |
| Cache hit speed | Time to answer from the cache | Response time on hits only | Under 100 ms |
| Answer quality | How correct the answers are | Eval-set score (AI judge or exact match) versus the always-large-model baseline | About equal; no significant drop |
| Route split | How traffic divides between small and large model | % simple, % complex, % escalated | Majority simple, quality preserved |
| False cache hits | Wrong answers served from cache | Count on the 50 near-miss pairs | Zero |
| Router accuracy | How often the router labels a question the same as a human | Agreement with 100 hand-labelled queries | Report the number; improve if low |

**Primary goal:** reduce cost and p95 latency while keeping quality equal to the baseline.

**Secondary goals:**

- Both team members understand every part of the system, not just their half
- Every result can be reproduced from a tagged commit and a fixed test set
- The repo is clean enough for a recruiter to understand in about one minute

## 3. Scope

The project covers building the plain RAG baseline plus the cache, router, escalation, logging, dashboard and comparison run. It does not cover production deployment or changes to how retrieval itself works.

**In scope**

- A plain RAG baseline: corpus, chunking, embeddings, vector store, retrieval, answer generation, FastAPI endpoint
- An eval set (50-100 questions) and an automated scoring script
- Request logging to SQLite (Postgres optional)
- Semantic cache with `corpus_version` and TTL, plus threshold tuning
- Rule-based router, with an optional small-LLM classifier to compare
- Escalation from the small to the large model when an answer looks weak
- Streamlit dashboard
- Baseline vs new-system comparison, including repeated and reworded questions
- README with measured results

**Out of scope (for the first version)**

- Full multi-tenant isolation beyond a simple tenant or user key (documented as future work)
- Automatic threshold re-tuning in production
- A/B testing infrastructure and online learning of the router
- Replacing or redesigning the retrieval pipeline
- Cloud deployment, authentication and user accounts

**Assumptions**

- We have API access (and budget) for at least one small and one large model, reachable through LiteLLM
- The corpus is a fixed set of 50-200 documents we are allowed to use
- Both of us can run Python 3 and Docker locally
- The baseline is built first and together; the 5-7 hour estimate for the cache and router work assumes it already exists

**Prerequisites before starting Phase 1**

1. Baseline pipeline answers questions end to end
2. Eval set exists and has been hand-checked
3. Scoring script has run at least once and saved a CSV
4. Logging schema is agreed by both of us

## 4. Team and roles

Two people build this: we work together on the baseline and the finish, and split the cache and router in the middle. Names are left as Person A and Person B until you decide who takes which half.

| Phase | Person A | Person B |
| --- | --- | --- |
| 0: Baseline | Pair on everything. Suggested lead: corpus, chunking, embeddings, vector DB, FastAPI | Pair on everything. Suggested lead: eval set, scoring script |
| 1: Improvements | Semantic cache, `corpus_version` and TTL, threshold tuning (100 pairs) | Router, 100 labelled queries, escalation |
| 2: Finish | Pair: dashboard, comparison run, README | Pair: dashboard, comparison run, README |

**Why pair on the baseline.** Every later decision depends on understanding chunking, embeddings, retrieval and the eval script. If we split too early, one of us ends up with a black box.

**The contract between the two halves.** The logging schema (Section 11) is the shared agreement. Both the cache and the router write to it, so we agree on it in Phase 0 and change it only together.

**GitHub workflow**

1. One repo; the other person is added as a collaborator.
2. `main` is protected: all changes arrive through pull requests.
3. One branch per task, named like `feat/semantic-cache` or `feat/router`.
4. We review each other's pull requests. This is how each of us learns the other half.
5. Tasks are tracked as GitHub Issues on a simple Projects board (Phase 0, 1, 2).
6. We tag important commits, for example `baseline-v1`, so results can be reproduced.
7. Secrets live in `.env` (git-ignored). The repo contains `.env.example` with placeholders only.

## 5. Glossary in plain language

Every term used in this document, with a definition and an example. Keep this open while reading the rest.

| Term | Plain meaning | Example |
| --- | --- | --- |
| RAG | Retrieval-Augmented Generation: look up relevant text first, then have an AI write an answer from it | Find the leave-policy paragraphs, then answer "15 days" |
| Corpus | The pile of documents the system answers from | A company handbook of 100 pages |
| Chunk | A small piece of a document (about 500 tokens) | One paragraph of the handbook |
| Token | A piece of a word; AI models count and charge by tokens | "vacation" is about 1-2 tokens |
| Embedding | A list of numbers that captures the meaning of text | "paid leave" and "vacation days" get similar numbers |
| Vector database | A store that finds the embeddings closest in meaning to a query | Qdrant |
| Retrieval (top-k) | Fetching the k closest chunks; we use k = 5 | The 5 chunks nearest the question |
| Semantic cache | Saved answers matched by meaning, not exact words | "reset my password" matches "password reset steps" |
| Similarity score | A 0 to 1 number for how close two embeddings are | 0.94 = very close |
| Threshold | The minimum similarity needed to reuse a cached answer | 0.92 |
| Paraphrase pair | Two questions worded differently that mean the same | "how do I reset my password" / "password reset steps" |
| Near-miss pair | Two similar-looking questions that need different answers | "refund policy in the EU" / "refund policy in the US" |
| `corpus_version` | A number stamped on each cached answer; bumped when documents change | v1 becomes v2 after re-uploading the handbook |
| TTL | Time to live: an expiry date on a cached answer | Expire after 7 days |
| Router | Labels a question simple or complex | "Wifi password?" = simple |
| Escalation | Redoing a question on the large model when the small model's answer looks weak | Small model says "I don't know", so the large model retries |
| Small / large model | A cheap, fast AI model vs an expensive, stronger one | Chosen through LiteLLM |
| LiteLLM | A library that calls many AI providers through one interface | Switch models by changing a name |
| Eval set | Test questions with correct answers and source documents | Our "test paper" |
| Baseline | The plain system before any upgrade; the "before" measurement | Always the large model, no cache |
| p50 / p95 | Typical response time / the slow end (95% of requests are faster) | p50 = 1.2 s, p95 = 3.5 s |
| Cache hit / miss | Answered from the cache / not found, so the full pipeline runs | A repeat question is a hit |
| Tenant | One customer or organization using the system | Company A vs Company B |

## 6. Architecture and request flow

Every question takes one of three paths: a cache hit, the small model, or the large model. Escalation is the only way one question ends up using both models.

&#91;embedded content: request flow · 3 decisions, 3 paths\]

The highlighted box is the cheapest path: no retrieval and no model call. A cache miss is routed to the small or large model, and a weak small-model answer is redone on the large model. Only cache misses are saved to the cache, and every path ends in the request log.

**Step by step**

1. The question arrives at the API.
2. It is normalized (lowercase, punctuation stripped) and embedded.
3. The cache is searched for the nearest earlier question. If similarity is at or above the threshold and `corpus_version` matches, the saved answer is returned and logged. Done.
4. On a miss, the router labels the question simple or complex.
5. Simple goes to the small model; complex goes to the large model. Both use the same retrieval step over the corpus.
6. If the small model's answer looks weak, the question is redone on the large model.
7. A clean answer is saved to the cache with its embedding, sources, timestamp and `corpus_version`.
8. The request is logged (cost, latency, route, escalation, cache hit) and the answer is returned.

**Core logic (pseudocode)**

```python
def answer(query: str) -> dict:
    q_vec = embed(normalize(query))
    hit = cache.nearest(q_vec)
    if hit and hit.score >= THRESHOLD and hit.version == CORPUS_VERSION:
        log_request(query, cache_hit=True)
        return hit.payload

    route = classify(query)  # "simple" or "complex"
    model = SMALL_MODEL if route == "simple" else LARGE_MODEL
    result = rag_pipeline(query, model=model)
    if route == "simple" and needs_escalation(result):
        result = rag_pipeline(query, model=LARGE_MODEL)

    if is_cacheable(result):  # never cache errors, empty or personalized answers
        cache.store(q_vec, result, version=CORPUS_VERSION)
    log_request(query, cache_hit=False, route=route, result=result)
    return result
```

**Components and where they live**

| Component | Job | Folder |
| --- | --- | --- |
| API | Receives questions, returns answers | `src/api/` |
| RAG pipeline | Chunk, embed, retrieve, generate with citations | `src/rag/` |
| Semantic cache | Lookup, store, versioning, TTL | `src/cache/` |
| Router and escalation | Simple vs complex; redo weak answers | `src/router/` |
| Request logger | Writes one row per request to SQLite | `src/logging/` |
| Dashboard | Charts built from the log | `src/dashboard/` |
| Scripts | Ingest, eval, threshold sweep, comparison | `scripts/` |

## 7. Phase 0: Baseline requirements (built together)

Phase 0 produces a plain RAG service, a test set, a grader and a log, so every later improvement has a "before" to compare against. Nothing in Phase 1 starts until Phase 0 is done.

**B1. Corpus**

- Use 50-200 real, slightly messy documents (a company handbook, product docs or a Wikipedia subset).
- Store them in a `data/corpus/` folder with a short note on the source and licence.
- Messy is good: it makes the eval honest.

**B2. RAG pipeline**

1. Chunk each document at about 500 tokens with overlap, so a sentence is not cut off from its context.
2. Embed each chunk with a sentence-transformers model.
3. Store the embeddings plus metadata (document id, chunk id, text) in the vector database.
4. For a question, embed it and retrieve the top 5 closest chunks.
5. Send the question and chunks to the large model; require an answer with citations (which chunk or document each claim came from).

The same embedding model must be used for the corpus and for queries, and later for the cache.

**B3. FastAPI endpoint**

- `POST /ask` takes a question and returns the answer, sources, model used, cost and latency.
- Add a `GET /health` check.
- Keep the pipeline in importable functions, so the scoring script and API call the same code.

**B4. Eval set (the most valuable file in the repo)**

- 50-100 questions, each with a reference answer and the source document.
- Cover easy and hard questions, so the router has something to sort later.
- If questions are AI-generated, one person writes or generates them and the other checks each by hand.
- Save as a versioned file such as `eval/eval_set.jsonl`. Never edit it after the baseline run without tagging a new version.

**B5. Scoring script**

- Runs every eval question through the pipeline.
- Scores answer correctness (an AI judge is fine; keep the judge prompt in the repo) and retrieval hit rate (did the right document appear in the top 5?).
- Writes a CSV with one row per question: question, answer, correct, retrieval hit, cost, latency.
- Must run with one command so we can re-run it after every change.

**B6. Request logging**

- Every request writes one row to SQLite using the schema in Section 11.
- Log from day one, even when the cache and router do not exist yet; those columns stay empty or default.

**B7. Baseline run**

- Run the full eval set and record cost per request, p50 and p95 latency and quality.
- Tag the commit `baseline-v1` and save the results CSV in `results/`.

**Phase 0 is done when:** the API answers questions with citations, the eval set is hand-checked, the scoring script has produced a CSV, logging works, and the baseline numbers are saved and tagged.

## 8. Phase 1A: Semantic cache requirements

The cache returns a saved answer when a new question means the same as an old one, and the underlying documents have not changed. Getting this wrong gives confident wrong answers, so correctness comes before hit rate.

**C1. Lookup flow**

1. Normalize the question: lowercase, strip punctuation and extra spaces.
2. Embed it with the same model used for the corpus.
3. Search the cache collection (Qdrant or Redis vector search) for the nearest earlier question.
4. If similarity is at or above the threshold **and** the entry's `corpus_version` equals the current version, return the stored answer and sources.
5. Otherwise run the full pipeline, then store the new entry.

**C2. What each cache entry stores**

- The query embedding and the original query text
- The answer and its sources
- A timestamp and a TTL (expiry)
- The `corpus_version` at the time it was made
- A `tenant_id` or `user_id` when answers depend on who asks

**C3. Invalidation (non-negotiable)**

- Bump `corpus_version` every time documents are re-ingested, so old answers stop being served.
- Add a TTL as a second safety net.
- Never cache errors, empty answers, "I don't know" answers, or answers that depend on who is asking.
- If answers are personalized, include the tenant or user in the cache key, or skip caching for those queries.

**C4. Threshold tuning (the step interviewers ask about)**

1. Write about 50 **paraphrase pairs** that should hit the cache. Example: "how do I reset my password" and "password reset steps".
2. Write about 50 **near-miss pairs** that must not hit. Example: "refund policy in the EU" and "refund policy in the US".
3. Sweep the threshold from 0.85 to 0.97 in small steps (for example 0.01).
4. At each value, count paraphrase pairs correctly matched and near-miss pairs wrongly matched.
5. Pick the **lowest threshold with zero false hits** on the near-miss set. A lower threshold means more savings, but only if no wrong answers slip through.
6. Save the pair files in `eval/` and record the chosen threshold and test-set sizes in the README.

If no threshold in the range gives zero false hits, raise the upper bound, rewrite ambiguous pairs, or consider a cheap second check (for example comparing key entities such as "EU" vs "US") before returning a hit.

**C5. Behavior and performance**

- A cache hit skips retrieval and the LLM call entirely, and is logged with `cache_hit = true`.
- Hit latency target: under 100 ms.
- Cache storage is separate from the document collection so the two never mix.

**C6. Tests**

- A paraphrase pair returns the cached answer.
- A near-miss pair does not.
- After bumping `corpus_version`, the same question runs the full pipeline.
- An expired entry is not served.
- An error response is never stored.

**Phase 1A is done when:** the cache is live, versioned and TTL-protected, the threshold is tuned with zero false hits on at least 50 + 50 pairs, and the tests above pass.

## 9. Phase 1B: Router and escalation requirements

The router sends easy questions to a cheap model and hard ones to a strong model, and escalation catches the cheap model's mistakes. Together they keep quality flat while most traffic stays cheap.

**R1. Model choices**

- Pick one small model and one large model, both called through LiteLLM.
- Keep model names and prices in a config file (`config/models.yaml`), never hard-coded.
- The baseline uses the large model for everything; the new system uses both.

**R2. Rule-based router (build this first)**

The router inspects each question and returns `simple` or `complex`. Signals to use:

| Signal | Looks complex when | Example |
| --- | --- | --- |
| Query length | Many words or tokens | A 40-word multi-part question |
| Entity or concept count | Several distinct things mentioned | "EU and US refund policies" |
| Complexity words | Contains compare, why, explain, difference, versus, summarize | "Explain why the policies differ" |
| Retrieval score spread | Top-5 scores vary widely, meaning no clear best chunk | Scores of 0.82, 0.55, 0.41, 0.40, 0.38 |

Keep the rules transparent: combine the signals into a simple score and a single threshold, and log which signals fired for each decision. That makes errors easy to debug.

**R3. Validating the router**

1. Hand-label about 100 real or realistic queries as simple or complex. Both of us label, and we discuss disagreements.
2. Run the router and compute accuracy (agreement with the labels).
3. Look at the mistakes. A complex question labelled simple hurts quality; a simple one labelled complex only wastes money, so tune to avoid the first.
4. Save the labelled file as `eval/router_labels.csv`.

**R4. Optional: tiny LLM classifier**

- After the rules work, try a tiny model that classifies each question.
- Compare it against the rules on accuracy **and** on its own cost, since it adds a call per request.
- Keep whichever gives the better cost and accuracy trade-off.

**R5. Escalation**

When the router sends a question to the small model, check the answer. Re-run on the large model if any of these is true:

- Retrieval scores are low (best chunk below a set value)
- The answer has no citation
- The answer says "I don't know" or similar

Log `escalated = true` and charge the cost of both calls, so savings are not overstated. Tune the escalation checks on the eval set so quality stays at baseline level.

**R6. Tests**

- Obvious simple and complex questions are routed as expected.
- A question with a weak small-model answer is escalated and the final answer comes from the large model.
- Escalated requests log both costs.

**Phase 1B is done when:** the rule-based router is validated on 100 labelled queries, escalation works and is tested, and routing decisions are logged.

## 10. Phase 2: Dashboard, comparison and README requirements (built together)

Phase 2 turns the working system into evidence: a dashboard that shows it working, a fair before/after comparison, and a README that tells the story in about one minute.

**D1. Streamlit dashboard**

Reads the SQLite log and shows:

- Cost per request, over time
- Cache hit rate
- Route split: simple vs complex vs escalated
- p50 and p95 latency
- Quality score per route, over time

It should refresh without manual steps and run with one command. A clean screenshot of it is the best image for the README.

**D2. Comparison run (the fair test)**

1. Fix the test traffic: the eval set plus **reworded versions** of it, to mimic real users repeating questions. Save this paraphrase set in the repo so the run is replayable.
2. Run it through the **baseline** (always the large model, no cache).
3. Run the same traffic through the **new system** (cache and router).
4. Compare: cost reduction in %, p50 and p95 change, cache hit rate, route split and the quality difference.
5. Save both results CSVs in `results/` and tag the commit.

Why repeats matter: testing only unique questions gives the cache no chance to help, and understates the savings.

**D3. Quality check**

Quality must be about equal to the baseline. Report the score for both systems on the same eval questions. If new-system quality is lower, tune escalation or the threshold before claiming savings.

**D4. README**

- Architecture diagram at the top
- Results table: baseline vs new system, with exact numbers from the scripts
- Dashboard screenshot or a short demo GIF
- One-command setup with `docker compose`
- How to run the eval and the comparison
- The chosen threshold and the test-set sizes
- A Limitations section stating plainly what does not work or was not tested
- The final resume line with real numbers (Section 17)

**Phase 2 is done when:** the dashboard works, the comparison has been run and recorded, and the README contains the measured numbers and a screenshot.

## 11. Data model

Two stores matter: a request log (SQLite, one row per request) and cache entries (in the vector store). The log schema is the contract between both halves of the project, so we agree on it in Phase 0 and change it only together.

**Request log table: `requests`**

| Column | Type | Meaning |
| --- | --- | --- |
| `id` | integer | Unique request id |
| `timestamp` | datetime | When the request arrived |
| `query` | text | The question as asked |
| `tenant_id` | text, optional | Who asked, when answers are personalized |
| `cache_hit` | boolean | Answered from the cache |
| `cache_score` | float, optional | Similarity of the nearest cached query |
| `route` | text | `simple`, `complex`, or `cache` |
| `router_signals` | text (JSON) | Which rules fired, for debugging |
| `model_used` | text | Final model that produced the answer |
| `escalated` | boolean | Small model answer was redone on the large model |
| `input_tokens` | integer | Total input tokens, including any escalation call |
| `output_tokens` | integer | Total output tokens, including any escalation call |
| `cost_usd` | float | Tokens × price table, both calls if escalated |
| `latency_ms` | integer | End-to-end response time |
| `quality_score` | float, optional | From the eval set, when the question is an eval question |
| `corpus_version` | integer | Version of the documents at answer time |
| `error` | text, optional | Error message if the request failed |

**Cache entry (stored in Qdrant or Redis)**

| Field | Meaning |
| --- | --- |
| vector | Embedding of the normalized query |
| `query_text` | The original question |
| `answer` | The stored answer |
| `sources` | Citations returned with the answer |
| `created_at` | Timestamp, used with the TTL |
| `ttl_seconds` | How long the entry is valid |
| `corpus_version` | Version of the documents when the answer was made |
| `tenant_id` | Optional; included in the lookup filter when answers are personalized |

**Price table (`config/models.yaml`)**

For each model: name, price per 1,000 input tokens, price per 1,000 output tokens. Cost is always computed from this file so prices can be updated in one place. Prices change often, so check the provider's current rates before the final comparison run.

**Eval and label files**

| File | Contents |
| --- | --- |
| `eval/eval_set.jsonl` | Question, reference answer, source document |
| `eval/paraphrase_pairs.csv` | About 50 pairs that should hit the cache |
| `eval/near_miss_pairs.csv` | About 50 pairs that must not hit |
| `eval/router_labels.csv` | About 100 queries labelled simple or complex |
| `eval/paraphrased_traffic.jsonl` | Reworded eval questions for the comparison run |

## 12. Tech stack and repo structure

Python end to end, with one tool per job. Each choice below is the recommended default; swap one only if there is a reason.

| Layer | Choice | Why |
| --- | --- | --- |
| Language | Python 3 | Standard for AI work and all libraries below |
| API | FastAPI | Typed, async, auto-generated docs |
| Vector store (corpus and cache) | Qdrant (or Redis) | Fast nearest-neighbor search with metadata filters |
| Embeddings | sentence-transformers | Runs locally; no per-call cost |
| Calling models | LiteLLM | One interface for many providers; easy to swap small and large models |
| Request logs | SQLite (dev), Postgres (optional later) | Simple, easy to query for the dashboard |
| Dashboard | Streamlit | Fast to build and screenshot-friendly |
| Tests | pytest | Standard and simple |
| Packaging | Docker and docker compose | One-command setup |
| Collaboration | GitHub | Shared repo, pull requests, issues |

**Suggested repo layout**

```
rag-cache-router/
  README.md
  docker-compose.yml
  .env.example
  .gitignore
  config/
    models.yaml          # model names and prices
    settings.yaml        # threshold, TTL, top-k, chunk size
  data/
    corpus/              # source documents
  eval/
    eval_set.jsonl
    paraphrase_pairs.csv
    near_miss_pairs.csv
    router_labels.csv
    paraphrased_traffic.jsonl
  src/
    api/                 # FastAPI app
    rag/                 # chunking, embedding, retrieval, generation
    cache/               # semantic cache
    router/              # classifier and escalation
    logging/             # request logger
    dashboard/           # Streamlit app
  scripts/
    ingest.py            # build the corpus index
    run_eval.py          # scoring script
    tune_threshold.py    # threshold sweep
    compare.py           # baseline vs new system
  results/               # CSVs from runs (small files only)
  tests/
```

**Git hygiene**

| Commit | Never commit |
| --- | --- |
| Code, configs, price table | API keys (use `.env`) |
| Eval set and pair files | Large datasets or model files |
| README and diagram | Vector DB data folders |
| `docker-compose.yml` | SQLite log files |

If an API key is ever pushed by mistake, revoke it immediately; deleting the commit is not enough.

## 13. Non-functional requirements

These are the qualities the system must have beyond "it works". Correctness comes first: a wrong cached answer is worse than no cache.

| Area | Requirement | How we check it |
| --- | --- | --- |
| Correctness | Zero false cache hits on the near-miss set | Threshold sweep script and the C6 tests |
| Isolation | Never return one tenant's or user's cached answer to another when answers are personalized | Include `tenant_id` or `user_id` in the cache key; add a test with two users |
| Observability | Every request, hit or miss, is logged with cost, latency and route | Row count in `requests` equals requests sent |
| Reproducibility | Evaluation runs can be replayed with the same results | Fixed eval and paraphrase files, tagged commits, fixed random seeds, model names recorded |
| Latency | Cache hits under 100 ms; overall p95 better than baseline | Dashboard and comparison run |
| Cost accuracy | Escalated requests count both model calls | Test on an escalated request |
| Quality | No significant drop versus the always-large baseline | Same eval set scored for both systems |
| Maintainability | Settings (threshold, TTL, top-k, model names, prices) live in config, not code | Code review |
| Security | No secrets in the repo; `.env` is git-ignored | `.gitignore` check and review before every push |
| Graceful failure | A failed model call returns a clear error and is logged, never cached | Test with a forced failure |
| Setup | A new person can run the project from the README with `docker compose up` | Partner follows the README on a clean clone |

**Privacy note.** The cache stores user questions and answers. If we ever use real user data, tell users, set a short TTL and avoid storing personal details in cached entries.

## 14. Risks and common mistakes

Most failures on this project come from skipping a measurement step, not from hard code. Each row below is a known trap with its fix.

| Risk or mistake | What goes wrong | Prevention |
| --- | --- | --- |
| Skipping the baseline | No "before" numbers, so no credible result | Phase 0 first; tag `baseline-v1` |
| Threshold too low | Different questions match, so users get confident wrong answers | Tune on near-miss pairs, not only paraphrases |
| Tuning on paraphrases only | The threshold looks great but fails on look-alike questions | Require zero false hits on the near-miss set |
| Caching personalized answers | Data leaks between users | Add `tenant_id` or `user_id` to the cache key, or skip caching |
| No `corpus_version` | Stale answers after documents change | Version every entry and bump on re-ingestion; add a TTL |
| Caching errors or empty answers | Later similar questions fail silently | Only cache successful, non-empty answers |
| Testing only unique questions | Cache looks useless; savings understated | Include reworded and repeated traffic |
| Ignoring escalation cost | Savings overstated | Count both calls on escalated requests |
| Router sends hard questions to the small model | Quality drops | Hand-label 100 queries; tune to avoid complex-as-simple errors |
| Weak or unchecked eval set | Quality claims are not trustworthy | Hand-check every reference answer |
| AI judge is inconsistent | Noisy quality scores | Keep the judge prompt fixed in the repo; spot-check a sample by hand |
| Price table out of date | Cost numbers are wrong | Re-check provider prices before the final run |
| Splitting too early | One partner does not understand half the system | Pair on Phase 0 and review each other's pull requests |
| Exposed API key | Account abuse and unexpected bills | `.env` plus `.gitignore`; revoke immediately if leaked |
| API rate limits or outages | Eval runs fail halfway | Retry with backoff; save partial results so runs can resume |
| Scope creep | Project never finishes | Keep extras in Section 17 until the acceptance criteria are met |

## 15. Timeline and task breakdown

The order is fixed by dependencies: baseline first, then the cache and router in parallel, then the finish. The source brief estimates 5-7 hours for the cache and router work on top of a working baseline. The baseline and the 250-plus hand-written test items (eval set, pairs, labels) add more, so the other hours below are our own rough guesses to revise after Phase 0. Dates are left open until you both agree a schedule.

| ID | Task | Owner | Depends on | Rough time |
| --- | --- | --- | --- | --- |
| **Phase 0: Baseline (together)** |  |  |  |  |
| 0.1 | Create GitHub repo, folder skeleton, `.gitignore`, `.env.example` | Either | None | 1 h |
| 0.2 | Choose and add the corpus | Both | 0.1 | 1-2 h |
| 0.3 | Chunking, embeddings, vector DB ingest | A | 0.2 | 2-3 h |
| 0.4 | Retrieval and answer generation with citations | A | 0.3 | 2-3 h |
| 0.5 | FastAPI `/ask` endpoint | A | 0.4 | 1-2 h |
| 0.6 | Write and hand-check the eval set (50-100 questions) | B | 0.2 | 3-5 h |
| 0.7 | Scoring script and CSV output | B | 0.4, 0.6 | 2-3 h |
| 0.8 | Agree the log schema and add request logging | Both | 0.5 | 1-2 h |
| 0.9 | Baseline run; record numbers; tag `baseline-v1` | Both | 0.7, 0.8 | 1 h |
| **Phase 1A: Cache (Person A)** |  |  |  |  |
| 1A.1 | Semantic cache: normalize, embed, lookup, store | A | 0.9 | 2-3 h |
| 1A.2 | `corpus_version` and TTL | A | 1A.1 | 1 h |
| 1A.3 | Write 50 paraphrase and 50 near-miss pairs | A | 0.9 | 2-3 h |
| 1A.4 | Threshold sweep and chosen value | A | 1A.1, 1A.3 | 1-2 h |
| 1A.5 | Cache tests (C6) | A | 1A.2 | 1 h |
| **Phase 1B: Router (Person B)** |  |  |  |  |
| 1B.1 | Model config through LiteLLM; small and large model | B | 0.9 | 1 h |
| 1B.2 | Rule-based router | B | 1B.1 | 2 h |
| 1B.3 | Hand-label 100 queries; measure accuracy | B | 1B.2 | 2-3 h |
| 1B.4 | Escalation logic and cost counting | B | 1B.2 | 1-2 h |
| 1B.5 | Router and escalation tests (R6) | B | 1B.4 | 1 h |
| 1B.6 | Optional: tiny LLM classifier comparison | B | 1B.3 | 2 h |
| **Phase 2: Finish (together)** |  |  |  |  |
| 2.1 | Merge cache and router into one request flow (Section 6) | Both | 1A.5, 1B.5 | 1-2 h |
| 2.2 | Streamlit dashboard | Both | 2.1 | 2-3 h |
| 2.3 | Build the reworded traffic set | Both | 0.6 | 1-2 h |
| 2.4 | Comparison run: baseline vs new system | Both | 2.1, 2.3 | 1-2 h |
| 2.5 | README, diagram, screenshot, resume line | Both | 2.2, 2.4 | 2-3 h |

**Milestones**

1. **M0:** Baseline numbers saved and tagged.
2. **M1:** Cache and router each pass their tests on separate branches.
3. **M2:** Merged system answers end to end and logs everything.
4. **M3:** Comparison run recorded; README complete.

Track these as GitHub Issues on a Projects board. Review progress together at each milestone.

## 16. Acceptance criteria (definition of done)

The project is finished when every box below is ticked. Tick them here as you go.

**Baseline**

- [ ] RAG pipeline answers questions with citations through the FastAPI endpoint
- [ ] Eval set of 50-100 questions exists and every reference answer is hand-checked
- [ ] Scoring script runs with one command and writes a CSV
- [ ] Request logging works and uses the agreed schema
- [ ] Baseline run is complete, numbers are saved, commit is tagged `baseline-v1`

**Semantic cache**

- [ ] Cache is live, versioned (`corpus_version`) and protected by a TTL
- [ ] Errors, empty answers and unisolated personalized answers are never cached
- [ ] Threshold tuned on at least 50 paraphrase and 50 near-miss pairs, with zero false hits
- [ ] Chosen threshold and test-set sizes are documented
- [ ] Cache tests (C6) pass

**Router and escalation**

- [ ] Rule-based router classifies queries; accuracy measured on about 100 hand-labelled queries
- [ ] Escalation is implemented and tested, and counts the cost of both calls
- [ ] Routing decisions are logged

**Dashboard and comparison**

- [ ] Dashboard shows cost per request, hit rate, route split, p50 and p95 latency, and quality over time
- [ ] Baseline and new system were both run on the eval set plus reworded traffic
- [ ] Cost reduction %, p95 change and quality difference are recorded

**Repo and README**

- [ ] README has the architecture diagram, results table, dashboard screenshot, one-command setup and Limitations
- [ ] README contains the measured X, Y and Z numbers and the resume line
- [ ] No secrets in the repo; `.env.example` is present
- [ ] Both of us can explain every part of the system in an interview

## 17. Resume line, future improvements and open questions

**Resume line (fill in after the comparison run)**

> Added semantic caching and cost-aware model routing to a RAG service, cutting LLM cost by **X%** and p95 latency by **Y%** with no drop in answer quality on a **Z**-question eval set.

Replace X, Y and Z only with numbers from our own recorded runs. Optionally add N, the number of reworded questions used. If a number is weak, report it honestly and explain it in Limitations; interviewers trust that more than an inflated claim.

**Optional improvements after the acceptance criteria are met**

- Adaptive threshold that drifts with the observed false-hit rate, with a hard safety floor
- Full multi-tenant cache isolation using `tenant_id` in the vector payload filter
- Online router that learns from escalation outcomes, or a small distilled classifier
- Cost budget or rate limiter that pushes more traffic to the small model when spend is high
- Shadow mode: run the large model on a sample of traffic in the background to track quality drift
- Automatic generation of near-miss pairs from the corpus (same intent, different entities)
- Entity check before returning a cache hit (for example EU vs US) as a second guard

**Open questions for you and your partner**

- [ ] Which corpus will we use, and are we allowed to use it?
- [ ] Which small and large models, and what budget for the eval runs?
- [ ] Qdrant or Redis for the vector store?
- [ ] Who takes Person A (cache) and who takes Person B (router)?
- [ ] What is our target finish date for each milestone?
- [ ] Is the target quality "equal" or "within a set margin" of the baseline, and how large a margin?
- [ ] Will answers ever be personalized, which would make tenant isolation required rather than optional?
