import pytest

from schemas import ScrapedContent
from tools.scrape import BaseScraper
from tools.scrape.firecrawl_budget import FirecrawlBudget
from tools.scrape.firecrawl_scraper import FirecrawlScraper
from tools.scrape.hybrid_scraper import HybridScraper


def test_firecrawl_scraper_extracts_markdown(monkeypatch):
    scraper = FirecrawlScraper(
        api_key="fc-test",
        enabled=True,
        budget=FirecrawlBudget(max_pages=1, max_credits=1),
    )

    monkeypatch.setattr(
        scraper,
        "_post_scrape",
        lambda payload: {
            "success": True,
            "data": {"markdown": " # Clean page\n\nUseful content. "},
        },
    )

    scraped = scraper.scrape("https://example.com")

    assert scraped.content == "# Clean page\n\nUseful content."
    assert scraper.budget.pages_used == 1
    assert scraper.budget.credits_used == 1


def test_firecrawl_scraper_requires_enabled_and_key():
    disabled = FirecrawlScraper(api_key="fc-test", enabled=False)
    with pytest.raises(RuntimeError, match="disabled"):
        disabled.scrape("https://example.com")

    missing_key = FirecrawlScraper(api_key=None, enabled=True)
    missing_key.api_key = None
    with pytest.raises(RuntimeError, match="FIRECRAWL_API_KEY"):
        missing_key.scrape("https://example.com")


class FailingScraper(BaseScraper):
    def scrape(self, url: str) -> ScrapedContent:
        raise ValueError("failed")


class SuccessfulScraper(BaseScraper):
    def scrape(self, url: str) -> ScrapedContent:
        return ScrapedContent(url=url, content="fallback content")


def test_hybrid_scraper_uses_fallback_when_primary_fails():
    scraper = HybridScraper(
        primary=FailingScraper(),
        fallback=SuccessfulScraper(),
    )

    scraped = scraper.scrape("https://example.com")

    assert scraped.content == "fallback content"
