from schemas import ScrapedContent
from .base import BaseScraper
from .firecrawl_scraper import FirecrawlScraper
from .general_web_scrapper import GeneralWebScraper


class HybridScraper(BaseScraper):
    def __init__(
        self,
        primary: BaseScraper | None = None,
        fallback: BaseScraper | None = None,
    ):
        self.primary = primary or GeneralWebScraper()
        self.fallback = fallback or FirecrawlScraper()

    def scrape(self, url: str) -> ScrapedContent:
        try:
            return self.primary.scrape(url)
        except (ValueError, TimeoutError, ConnectionError, OSError):
            return self.fallback.scrape(url)
