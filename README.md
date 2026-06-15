# DeepResearch CreateAgent

A production-oriented DeepResearch prototype built around a multi-agent research workflow:

```text
Plan -> Distribute -> Research -> Reflect -> Synthesize -> Generate Report -> Critique -> Refine -> Output
```

The current implementation is a CLI pipeline. It plans a user query into structured research tasks, runs task research
in parallel, validates coverage through reflection, synthesizes the evidence, drafts a report, critiques it, and
produces a refined Markdown report.

## Current Capabilities

- Structured planning with `ResearchTask` objects instead of plain strings.
- Parallel research execution through `TaskDistributionAgent`.
- Web retrieval through DuckDuckGo search and Trafilatura scraping.
- Source metadata preservation: source ID, URL, domain, snippet, rank, provider, content length, and fetch timestamp.
- Citation-first research responses with source IDs.
- Reflection loop that can request follow-up research tasks.
- Synthesis stage that builds an evidence map before report generation.
- Separate report, critique, and refinement agents to reduce self-review bias.
- Deterministic retrieval unit test using fake search/scrape providers.

## Workflow

1. `Planner Agent`
    - Converts the user query into structured research tasks.
    - Each task includes an ID, question, objective, expected output, priority, dependencies, and suggested search
      queries.

2. `Task Distribution Agent`
    - Runs research tasks concurrently.
    - Isolates task failures so one failed task does not crash the full research run.

3. `Research Agent`
    - Runs search queries for each task.
    - Scrapes relevant pages.
    - Produces structured findings with citations and source IDs.

4. `Reflection Agent`
    - Checks whether each task result is complete.
    - Flags weak sources, contradictions, gaps, and missing topics.
    - Can create follow-up tasks when evidence is insufficient.

5. `Synthesis Agent`
    - Merges validated research results into an evidence map.
    - Deduplicates themes and keeps unresolved conflicts visible.

6. `Report Generation Agent`
    - Creates the initial Markdown research report from synthesized evidence.

7. `Critique Agent`
    - Reviews the draft for factual accuracy, citation coverage, completeness, unsupported claims, and logical issues.

8. `Refinement Agent`
    - Applies critique feedback and produces the final polished report.

## Project Structure

```text
.
├── main.py                         # CLI entry point and full pipeline wiring
├── config.py                       # Environment-backed runtime config
├── agents/
│   ├── planner.py                  # Query decomposition
│   ├── distributor.py              # Parallel task execution
│   ├── research.py                 # Retrieval-backed research worker
│   ├── reflection.py               # Research quality review
│   ├── synthesis.py                # Evidence map generation
│   ├── report.py                   # Draft report generation
│   ├── critique.py                 # Independent report review
│   └── refinement.py               # Final report refinement
├── prompts/
│   ├── planner/current.md
│   ├── research/current.md
│   ├── reflection/current.md
│   ├── synthesis/current.md
│   ├── report/current.md
│   ├── critique/current.md
│   └── refinement/current.md
├── schemas/
│   ├── agent_modals.py             # Agent and report Pydantic schemas
│   └── retrieval_modals.py         # Search, scrape, and source schemas
├── tools/
│   ├── search/duckduckgo.py        # DuckDuckGo search provider
│   ├── scrape/trafilatura_scrapper.py
│   └── retrieval/service.py        # Search + scrape orchestration
├── tests/
│   └── test_retrieval.py
└── output/
    └── research_report.txt         # Generated final report
```

## Core Data Contracts

The pipeline passes structured Pydantic objects between stages:

- `ResearchTask`
- `Plan`
- `SearchResult`
- `SourceDocument`
- `Citation`
- `ResearchFinding`
- `ResearchResponse`
- `ReflectionResponse`
- `SynthesisResponse`
- `ReportResponse`
- `CritiqueResponse`
- `RefinementResponse`

This is intentional. DeepResearch quality depends on traceable artifacts, not loose prose passed between agents.

## Configuration

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your_openai_key
OPENAI_DEFAULT_MODEL=your_model_name
SEARCH_PROVIDER=duckduckgo
SCRAPER_PROVIDER=trafilatura
SEARCH_MAX_RESULTS=10
```

The current configured providers are:

- Search: `duckduckgo`
- Scraper: `trafilatura`

## Running

Install dependencies with your preferred project workflow. This repo uses `pyproject.toml` and includes a local virtual
environment in development.

Run the CLI pipeline:

```bash
.venv/bin/python main.py
```

The default query is currently hardcoded in `main.py`:

```python
"""Tell me which coffee beans should we use to make the best cold coffee. I live in India."""
```

The final Markdown report is written to:

```text
output/research_report.txt
```

Development limits are currently set in `main.py`:

```python
MAX_TASKS = 2
MAX_RESEARCH_WORKERS = 4
```

Increase `MAX_TASKS` when you are ready to run deeper research.

## Testing

Run the test suite:

```bash
.venv/bin/pytest -q
```

The retrieval test uses fake providers, so it does not depend on network availability.

## Current Limitations

- The orchestration is currently wired in `main.py`, not LangGraph.
- There is no API server yet.
- There is no persistent run storage yet.
- There is no vector-store or document-ingestion pipeline yet.
- There is no streaming progress API yet.
- Live execution requires working search/network access and valid OpenAI credentials.
- The query is currently hardcoded in `main.py`.

## Roadmap

- Move orchestration from `main.py` into `graph/research_graph.py`.
- Add run state models under `state/`.
- Add persistence for runs, tasks, sources, findings, critiques, and reports.
- Add API endpoints for starting research and checking status.
- Add streaming progress events.
- Add retries, timeouts, cancellation, and rate-limit handling.
- Add source cache and duplicate-source handling across runs.
- Add optional vector retrieval over uploaded/local documents.
- Add report export formats such as PDF and HTML.
- Add cost, token, and latency tracking.

## License

MIT
