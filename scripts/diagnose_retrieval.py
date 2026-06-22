import argparse

from config import config
from tools import RetrievalService, get_scraper, get_search_provider


def main() -> None:
    parser = argparse.ArgumentParser(description="Diagnose search + scrape retrieval.")
    parser.add_argument("query", help="Query to retrieve.")
    parser.add_argument("--max-results", type=int, default=3)
    parser.add_argument("--preview-chars", type=int, default=500)
    args = parser.parse_args()

    scraper = get_scraper()
    service = RetrievalService(
        search_provider=get_search_provider(),
        scraper=scraper,
    )

    print(f"Search provider: {config.SEARCH_PROVIDER}")
    print(f"Scraper provider: {config.SCRAPER_PROVIDER}")
    print(f"Firecrawl enabled: {config.FIRECRAWL_ENABLED}")
    print(f"Max results: {args.max_results}")
    print()

    documents = service.retrieve(args.query, max_results=args.max_results)
    print(f"Documents retrieved: {len(documents)}")

    for index, document in enumerate(documents, start=1):
        preview = " ".join(document.content[: args.preview_chars].split())
        print()
        print(f"[{index}] {document.title}")
        print(f"URL: {document.url}")
        print(f"Domain: {document.domain}")
        print(f"Content length: {document.content_length}")
        print(f"Preview: {preview}")


if __name__ == "__main__":
    main()
