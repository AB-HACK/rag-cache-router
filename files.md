What should we work on first?

1

2

3

4

Check the weekend quiz when I miss days
Files you already have
PRD (the doc)
TASK_DIVISION.md
AGENT.md
Files to create next

Needed before Abdul starts Phase 0

File	What it is	Why
README.md (skeleton)	Project title, one-paragraph goal, setup steps, empty results table	The repo’s front page; you fill in the numbers at the end
.gitignore	List of files Git should never commit	Keeps API keys, data folders and log files out of GitHub
.env.example	Placeholder API keys and settings	Shows the other person what to fill in, with no real secrets
docker-compose.yml	Starts Qdrant (and optionally Redis) with one command	Gives both of you the same setup
pyproject.toml	Python dependencies and lint settings	Makes installs identical on both machines
config/settings.yaml	Threshold, TTL, top-k, chunk size, corpus_version	The rules say these live in config, not code
config/models.yaml	Small and large model names and their prices	Cost is calculated from this file

Needed for the shared contract

File	What it is	Why
src/logging/schema.sql	The requests table definition	Both halves write to it, so it must be fixed early
eval/ file templates	Column headers and example rows for the eval set, paraphrase pairs, near-miss pairs and router labels	Samad and Abdul write their test data in the same format
data/corpus/SOURCES.md	Where the documents came from and their licence	Shows the data is legitimate

Helpful for teamwork

File	What it is	Why
.github/pull_request_template.md	A checklist shown on every pull request (task ID, tests, results re-run)	Makes the review habit easy
docs/DECISIONS.md	A short log of choices: Qdrant vs Redis, which models, which corpus	Stops you re-debating decisions
docs/baseline.md	Abdul’s notes on chunk size, embedding model and how scoring works	Gives Samad the explanation he needs for his catch-up

Later, in Phase 2

Architecture diagram image (the README needs it)
Dashboard screenshot
results/ CSVs from the baseline and comparison runs
My suggestion

Abdul needs the first group (the 7 files) to start. If you’d like, I can write all of them now, with sensible starter contents, as one scaffold you can drop into the repo. I can also write the second group (log schema and eval templates) in the same pass.
Test a brand-new account, sign-up to first cards

Check my streak around midnight

Clean warnings and test a release build

If I only read a few days in a week, how long should the weekend quiz be?

Short: only that week's words

Full length: add older words I've read

Don't open the quiz that week

1

2

3