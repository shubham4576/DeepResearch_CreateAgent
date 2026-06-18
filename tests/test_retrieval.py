from schemas import ScrapedContent, SearchResult
from memory.in_memory_store import InMemoryStore
from tools import RetrievalService
from tools.retrieval import RetrievalTools
from tools.scrape import BaseScraper
from tools.search import BaseSearchProvider


class FakeSearchProvider(BaseSearchProvider):
    def search(self, query: str, max_results: int) -> list[SearchResult]:
        return [
            SearchResult(
                title="Kafka Architecture",
                url="https://example.com/kafka-architecture",
                snippet="Kafka architecture overview.",
                rank=1,
                provider="fake",
            )
        ]


class FakeScraper(BaseScraper):
    def scrape(self, url: str) -> ScrapedContent:
        return ScrapedContent(
            url=url,
            content="Kafka uses brokers, topics, partitions, and replication.",
        )


def test_retrieval_preserves_source_metadata():
    service = RetrievalService(
        search_provider=FakeSearchProvider(),
        scraper=FakeScraper(),
    )

    documents = service.retrieve(
        query="Apache Kafka architecture",
        max_results=3,
    )

    assert len(documents) == 1

    document = documents[0]
    assert document.id
    assert document.title == "Kafka Architecture"
    assert document.url == "https://example.com/kafka-architecture"
    assert document.domain == "example.com"
    assert document.snippet == "Kafka architecture overview."
    assert document.rank == 1
    assert document.provider == "fake"
    assert document.content_length == len(document.content)


def test_retrieval_service_exposes_search_and_scrape_steps():
    service = RetrievalService(
        search_provider=FakeSearchProvider(),
        scraper=FakeScraper(),
    )

    results = service.search("Apache Kafka architecture", max_results=3)
    document = service.scrape(results[0])

    assert len(results) == 1
    assert document is not None
    assert document.title == "Kafka Architecture"


def test_retrieval_tools_store_sources_and_tool_calls():
    service = RetrievalService(
        search_provider=FakeSearchProvider(),
        scraper=FakeScraper(),
    )
    memory_store = InMemoryStore()
    tools = RetrievalTools(
        retrieval_service=service,
        memory_store=memory_store,
        run_id="run_1",
    )

    documents = tools.retrieve_web("Apache Kafka architecture", max_results=3)

    assert len(documents) == 1
    assert len(memory_store.list_sources("run_1")) == 1
    tool_calls = memory_store.list_tool_calls("run_1")
    assert len(tool_calls) == 1
    assert tool_calls[0].tool_name == "retrieve_web"
