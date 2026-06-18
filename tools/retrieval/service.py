import logging
from urllib.parse import urlparse
from uuid import uuid5, NAMESPACE_URL

from tqdm.auto import tqdm

from schemas import SearchResult, SourceDocument
from tools.scrape import BaseScraper
from tools.search import BaseSearchProvider

logger = logging.getLogger(__name__)


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
        except (ValueError, TimeoutError, ConnectionError, OSError) as error:
            logger.warning("Failed to scrape %s: %s", result.url, error)
            return None

    def search(self, query: str, max_results=10) -> list[SearchResult]:
        return self.search_provider.search(query, max_results)

    def scrape(self, result: SearchResult) -> SourceDocument | None:
        return self._scrape_document(result)

    def retrieve(self, query: str, max_results=10) -> list[SourceDocument]:
        search_results = self.search(query, max_results)

        documents: list[SourceDocument] = []

        for result in tqdm(
            search_results,
            desc=f"Scraping: {query[:40]}",
            leave=False,
        ):
            document = self.scrape(result)

            if document:
                documents.append(document)

        return documents
