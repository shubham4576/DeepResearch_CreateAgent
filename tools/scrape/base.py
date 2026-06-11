from abc import ABC, abstractmethod

from schemas import ScrapedContent


class BaseScraper(ABC):
    @abstractmethod
    def scrape(self, url: str) -> ScrapedContent:
        pass
