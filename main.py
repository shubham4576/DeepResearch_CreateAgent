from tools import RetrievalService, get_search_provider, get_scraper


def main():

    retrieval_service = RetrievalService(
        search_provider=get_search_provider(),
        scraper=get_scraper(),
    )

    query = "Research Apache Kafka architecture, workflow, scalability, and comparison with RabbitMQ."

    documents = retrieval_service.retrieve(
        query=query,
        max_results=5,
    )

    print(f"\nRetrieved {len(documents)} documents\n")

    for idx, document in enumerate(documents, start=1):

        print("=" * 80)
        print(f"DOCUMENT {idx}")
        print("=" * 80)

        print(f"TITLE: {document.title}")
        print(f"URL: {document.url}")

        preview = document.content[:1000]

        print("\nCONTENT PREVIEW:\n")
        print(preview)

        print("\n")


if __name__ == "__main__":
    main()
