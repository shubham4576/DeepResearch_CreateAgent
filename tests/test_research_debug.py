from schemas import ResearchResponse, ScrapedContent, SearchResult
from tools import RetrievalService
from tools.scrape import BaseScraper
from tools.search import BaseSearchProvider


class FakeSearchProvider(BaseSearchProvider):
    def search(self, query: str, max_results: int) -> list[SearchResult]:
        return [
            SearchResult(
                title="Kafka Source",
                url="https://example.com/kafka",
                snippet="Kafka snippet.",
                rank=1,
                provider="fake",
            )
        ]


class FakeScraper(BaseScraper):
    def scrape(self, url: str) -> ScrapedContent:
        return ScrapedContent(
            url=url,
            content="Kafka uses partitions and brokers for scalable logs.",
        )


def test_research_agent_writes_debug_context(monkeypatch, tmp_path):
    import agents.research as research_module
    from agents.research import ResearchAgent

    monkeypatch.setattr(research_module.config, "DEBUG_RESEARCH_CONTEXT", True)
    monkeypatch.setattr(research_module.config, "DEBUG_OUTPUT_PATH", tmp_path)
    monkeypatch.setattr(research_module, "make_llm", lambda **kwargs: object())

    class FakeAgent:
        def invoke(self, payload):
            return {
                "structured_response": ResearchResponse(
                    task_id="task_001",
                    task="Research Kafka",
                    summary="Kafka summary.",
                )
            }

    monkeypatch.setattr(
        research_module,
        "create_agent",
        lambda **kwargs: FakeAgent(),
    )

    service = RetrievalService(
        search_provider=FakeSearchProvider(),
        scraper=FakeScraper(),
    )

    ResearchAgent(service).execute("Research Kafka")

    debug_file = tmp_path / "research_context_task_001.md"
    debug_text = debug_file.read_text(encoding="utf-8")

    assert "## User Payload Sent To Research Agent" in debug_text
    assert "Research Question:" in debug_text
    assert "Research Kafka" in debug_text
    assert "Kafka uses partitions and brokers" in debug_text
    assert "https://example.com/kafka" in debug_text
