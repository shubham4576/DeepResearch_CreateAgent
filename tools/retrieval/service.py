from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
from uuid import uuid5, NAMESPACE_URL

from schemas import SearchResult, SourceDocument
from tools.scrape import BaseScraper
from tools.search import BaseSearchProvider


class RetrievalService:

    def __init__(self, search_provider: BaseSearchProvider, scraper: BaseScraper):
        self.search_provider = search_provider
        self.scraper = scraper

    def _scrape_document(self, result: SearchResult) -> SourceDocument | None:

        try:
            scraped = self.scraper.scrape(result.url)

            if not scraped.content:
                return None

            return SourceDocument(
                id=str(uuid5(NAMESPACE_URL, result.url)),
                title=result.title,
                url=result.url,
                domain=urlparse(result.url).netloc,
                snippet=result.snippet,
                rank=result.rank,
                provider=result.provider,
                content=scraped.content,
                content_length=len(scraped.content),
                fetched_at=scraped.fetched_at,
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
                    result,
                )
                for result in search_results
            ]

            for future in as_completed(futures):
                document = future.result()

                if document:
                    documents.append(document)

        return documents
