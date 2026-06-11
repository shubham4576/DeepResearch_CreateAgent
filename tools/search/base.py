from abc import ABC, abstractmethod

from schemas import SearchResult


class BaseSearchProvider(ABC):

    @abstractmethod
    def search(self, query: str, max_results: int) -> list[SearchResult]:
        pass
