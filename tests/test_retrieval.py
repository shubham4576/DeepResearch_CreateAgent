from schemas import ScrapedContent, SearchResult
from tools import RetrievalService
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
