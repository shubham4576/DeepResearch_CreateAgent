import pytest

from schemas import ScrapedContent
from tools.scrape import BaseScraper
from tools.scrape.firecrawl_budget import FirecrawlBudget, FirecrawlBudgetExceeded
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


def test_firecrawl_scraper_refunds_budget_on_failed_request(monkeypatch):
    scraper = FirecrawlScraper(
        api_key="fc-test",
        enabled=True,
        budget=FirecrawlBudget(max_pages=1, max_credits=1),
    )

    def fail(payload):
        raise ConnectionError("network failed")

    monkeypatch.setattr(scraper, "_post_scrape", fail)

    with pytest.raises(ConnectionError):
        scraper.scrape("https://example.com")

    assert scraper.budget.pages_used == 0
    assert scraper.budget.credits_used == 0


def test_firecrawl_budget_raises_explicit_exception():
    budget = FirecrawlBudget(max_pages=1, max_credits=1)
    budget.reserve_usage()

    with pytest.raises(FirecrawlBudgetExceeded):
        budget.reserve_usage()


def test_firecrawl_scraper_can_disable_local_budget_check(monkeypatch):
    scraper = FirecrawlScraper(
        api_key="fc-test",
        enabled=True,
        disable_budget_check=True,
        budget=FirecrawlBudget(max_pages=0, max_credits=0),
    )

    monkeypatch.setattr(
        scraper,
        "_post_scrape",
        lambda payload: {
            "success": True,
            "data": {"markdown": "content despite local zero budget"},
        },
    )

    scraped = scraper.scrape("https://example.com")

    assert scraped.content == "content despite local zero budget"
    assert scraper.budget.pages_used == 0
    assert scraper.budget.credits_used == 0


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
