from schemas import ScrapedContent
from .base import BaseScraper


class Newspaper4kScraper(BaseScraper):

    def scrape(self, url: str) -> ScrapedContent:
        try:
            import newspaper
        except ImportError as error:
            raise ImportError(
                "newspaper4k is not installed. Install it with `uv add newspaper4k` "
                "or `pip install newspaper4k`."
            ) from error

        article = newspaper.article(url)
        content = article.text

        if not content:
            raise ValueError(f"Failed to extract article text from {url}")

        return ScrapedContent(
            url=url,
            content=content,
        )
