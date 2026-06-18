import json
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from config import config
from schemas import ScrapedContent
from .base import BaseScraper
from .firecrawl_budget import FirecrawlBudget


class FirecrawlScraper(BaseScraper):
    API_URL = "https://api.firecrawl.dev/v2/scrape"

    def __init__(
        self,
        api_key: str | None = None,
        enabled: bool | None = None,
        budget: FirecrawlBudget | None = None,
    ):
        secret = config.FIRECRAWL_API_KEY
        self.api_key = api_key or (secret.get_secret_value() if secret else None)
        self.enabled = config.FIRECRAWL_ENABLED if enabled is None else enabled
        self.budget = budget or FirecrawlBudget(
            max_pages=config.FIRECRAWL_MAX_PAGES_PER_RUN,
            max_credits=config.FIRECRAWL_MAX_CREDITS_PER_RUN,
        )

    def scrape(self, url: str) -> ScrapedContent:
        self._validate_url(url)
        if not self.enabled:
            raise RuntimeError("Firecrawl is disabled. Set FIRECRAWL_ENABLED=true.")
        if not self.api_key:
            raise RuntimeError("FIRECRAWL_API_KEY is required for Firecrawl scraping.")

        self.budget.ensure_available(estimated_credits=1)
        payload = {
            "url": url,
            "formats": ["markdown"],
            "onlyMainContent": True,
            "removeBase64Images": True,
            "blockAds": True,
            "timeout": 60000,
        }
        response = self._post_scrape(payload)
        markdown = self._extract_markdown(response, url)
        self.budget.record_usage(estimated_credits=1)

        return ScrapedContent(
            url=url,
            content=markdown,
        )

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"Unsupported URL: {url}")

    def _post_scrape(self, payload: dict) -> dict:
        request = Request(
            self.API_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=75) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")
            raise ConnectionError(
                f"Firecrawl HTTP {error.code}: {self._firecrawl_error_hint(error.code)} {detail[:300]}"
            ) from error
        except URLError as error:
            raise ConnectionError(f"Firecrawl request failed: {error}") from error

        try:
            return json.loads(raw)
        except json.JSONDecodeError as error:
            raise ValueError("Firecrawl returned invalid JSON") from error

    def _extract_markdown(self, response: dict, url: str) -> str:
        if not response.get("success", False):
            raise ValueError(f"Firecrawl scrape failed for {url}: {response}")

        data = response.get("data") or {}
        markdown = data.get("markdown")
        if not markdown:
            raise ValueError(f"Firecrawl returned no markdown for {url}")

        return markdown.strip()

    def _firecrawl_error_hint(self, status_code: int) -> str:
        return {
            401: "Check FIRECRAWL_API_KEY.",
            402: "Insufficient Firecrawl credits.",
            429: "Firecrawl rate limit or concurrency limit exceeded.",
        }.get(status_code, "Request failed.")
