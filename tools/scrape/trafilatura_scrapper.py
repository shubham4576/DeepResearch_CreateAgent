import trafilatura

from schemas import ScrapedContent
from .base import BaseScraper


class TrafilaturaScraper(BaseScraper):

    def scrape(self, url: str) -> ScrapedContent:

        downloaded = trafilatura.fetch_url(
            url=url,
        )

        if not downloaded:
            raise ConnectionError(f"Failed to fetch URL: {url}")

        content = trafilatura.extract(downloaded)

        if content is None:
            raise ValueError(f"Failed to extract content from {url}")

        return ScrapedContent(
            url=url,
            content=content,
        )
