from tools import RetrievalService, get_search_provider, get_scraper


def test_retrieval():

    service = RetrievalService(
        search_provider=get_search_provider(),
        scraper=get_scraper(),
    )

    documents = service.retrieve(
        query="Apache Kafka architecture",
        max_results=3,
    )

    assert len(documents) > 0

    for document in documents:

        assert document.title
        assert document.url
        assert document.content
