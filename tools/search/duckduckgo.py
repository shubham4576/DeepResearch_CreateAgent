from ddgs import DDGS

from schemas import SearchResult
from .base import BaseSearchProvider


class DuckDuckGoSearchProvider(BaseSearchProvider):

    def search(self, query: str, max_results: int) -> list[SearchResult]:

        results = DDGS().text(
            query,
            max_results=max_results,
        )

        return [
            SearchResult(
                title=r["title"],
                url=r["href"],
                snippet=r["body"],
                rank=index,
                provider="duckduckgo",
            )
            for index, r in enumerate(results, start=1)
        ]
