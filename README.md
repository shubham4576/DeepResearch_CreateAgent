# DeepResearch POC

A multi-agent deep research system powered by LangChain and LangGraph. Users enter a query and the system autonomously searches the web, crawls relevant pages, retrieves from indexed knowledge, and synthesizes a structured, cited summary — similar to how Google and ChatGPT deep research work.

---

## How It Works

1. User submits a research query
2. The **Orchestrator Agent** decomposes it into sub-questions
3. Three specialized agents run **in parallel**:
   - **Web Search Agent** — queries Tavily / SerpAPI
   - **Deep Crawl Agent** — scrapes and extracts page content
   - **Knowledge Agent** — retrieves from a local vector store via RAG
4. The **Synthesis Agent** deduplicates, ranks, and drafts a final answer
5. The **Output Formatter** returns a structured Markdown summary with citations

---

## Project Structure

```
deepresearch-poc/
│
├── main.py                      # Entry point (CLI or FastAPI)
├── config.py                    # API keys, model names, env config
├── requirements.txt
├── .env
│
├── agents/
│   ├── orchestrator.py          # Query decomposition + agent coordination
│   ├── web_search_agent.py      # Web search via Tavily / SerpAPI
│   ├── deep_crawl_agent.py      # Page scraping + content extraction
│   ├── knowledge_agent.py       # RAG over indexed documents
│   └── synthesis_agent.py       # Merges results, drafts final answer
│
├── tools/
│   ├── search_tools.py          # LangChain-wrapped search API tools
│   ├── scraper_tools.py         # Playwright / BeautifulSoup tools
│   └── vector_tools.py          # Embedding + vector store retrieval
│
├── graph/
│   └── research_graph.py        # LangGraph StateGraph wiring all agents
│
├── state/
│   └── research_state.py        # Shared TypedDict state across agents
│
├── memory/
│   └── shared_memory.py         # Cross-agent memory (Redis / in-memory)
│
├── output/
│   └── formatter.py             # Markdown output, citations, confidence
│
├── api/
│   ├── router.py                # FastAPI routes (/research, /status)
│   └── schemas.py               # Pydantic request/response models
│
└── tests/
    ├── test_agents.py
    ├── test_tools.py
    └── test_graph.py
```

---

## Tech Stack

| Layer | Library |
|---|---|
| Agent orchestration | `langgraph`, `langchain` |
| Web search | `tavily-python` / `serpapi` |
| Web scraping | `playwright`, `trafilatura` |
| Vector store | `chromadb` / `qdrant-client` |
| Embeddings | `langchain-openai` |
| LLM | `gpt-4o` via OpenAI API |
| API layer | `fastapi`, `uvicorn` |
| Observability | `langsmith` |

---

## Getting Started

### 1. Clone the repo

```bash
git clone https://github.com/your-org/deepresearch-poc.git
cd deepresearch-poc
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 3. Set up environment variables

```bash
cp .env.example .env
```

Fill in your `.env`:

```env
OPENAI_API_KEY=your_openai_key
TAVILY_API_KEY=your_tavily_key
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_TRACING_V2=true
```

### 4. Run the API server

```bash
uvicorn main:app --reload
```

### 5. Make a research request

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the latest advancements in quantum computing in 2025?"}'
```

---

## Example Response

```json
{
  "query": "What are the latest advancements in quantum computing in 2025?",
  "summary": "...",
  "citations": [
    { "title": "...", "url": "...", "relevance_score": 0.94 }
  ],
  "confidence": 0.87,
  "sources_searched": 12
}
```

---

## Roadmap

- [ ] Parallel agent execution via LangGraph fan-out
- [ ] Streaming response support (SSE)
- [ ] Frontend UI (React + Tailwind)
- [ ] PDF / document ingestion pipeline
- [ ] Query history and session memory
- [ ] Docker + deployment setup

---

## License

MIT