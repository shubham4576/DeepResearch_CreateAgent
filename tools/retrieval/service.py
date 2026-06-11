from concurrent.futures import ThreadPoolExecutor, as_completed

from schemas import SourceDocument
from tools.scrape import BaseScraper
from tools.search import BaseSearchProvider


class RetrievalService:

    def __init__(self, search_provider: BaseSearchProvider, scraper: BaseScraper):
        self.search_provider = search_provider
        self.scraper = scraper

    def _scrape_document(self, title: str, url: str) -> SourceDocument | None:

        try:
            scraped = self.scraper.scrape(url)

            if not scraped.content:
                return None

            return SourceDocument(
                title=title,
                url=url,
                content=scraped.content,
            )
        except Exception:
            return None

    def retrieve(self, query: str, max_results=10) -> list[SourceDocument]:
        search_results = self.search_provider.search(query, max_results)

        documents: list[SourceDocument] = []

        with ThreadPoolExecutor(max_workers=5) as executor:

            futures = [
                executor.submit(
                    self._scrape_document,
                    result.title,
                    result.url,
                )
                for result in search_results
            ]

            for future in as_completed(futures):
                document = future.result()

                if document:
                    documents.append(document)

        return documents
