from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import trafilatura

from schemas import ScrapedContent
from .base import BaseScraper


class _VisibleTextParser(HTMLParser):
    """Small fallback extractor for pages that are not article-shaped."""

    _SKIPPED_TAGS = {"script", "style", "noscript", "svg", "canvas"}
    _BLOCK_TAGS = {
        "article",
        "aside",
        "blockquote",
        "br",
        "dd",
        "div",
        "dl",
        "dt",
        "figcaption",
        "footer",
        "form",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "header",
        "hr",
        "li",
        "main",
        "nav",
        "ol",
        "p",
        "pre",
        "section",
        "table",
        "td",
        "th",
        "tr",
        "ul",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self._skip_depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs):
        if tag in self._SKIPPED_TAGS:
            self._skip_depth += 1
        elif tag in self._BLOCK_TAGS:
            self._parts.append("\n")

    def handle_endtag(self, tag: str):
        if tag in self._SKIPPED_TAGS and self._skip_depth:
            self._skip_depth -= 1
        elif tag in self._BLOCK_TAGS:
            self._parts.append("\n")

    def handle_data(self, data: str):
        if self._skip_depth:
            return
        text = " ".join(data.split())
        if text:
            self._parts.append(text)

    def get_text(self) -> str:
        lines = []
        previous = ""
        for line in " ".join(self._parts).splitlines():
            cleaned = " ".join(line.split())
            if cleaned and cleaned != previous:
                lines.append(cleaned)
                previous = cleaned
        return "\n".join(lines).strip()


class GeneralWebScraper(BaseScraper):
    """General-purpose local scraper for mixed web pages.

    It deliberately avoids browser cookies and third-party reader services.
    """

    _USER_AGENT = (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    )
    _MIN_CONTENT_LENGTH = 200
    _MAX_BYTES = 5_000_000

    def scrape(self, url: str) -> ScrapedContent:
        self._validate_url(url)
        html = self._fetch(url)

        content = self._extract_with_trafilatura(html, url)
        if not content:
            content = self._extract_visible_text(html)

        if len(content) < self._MIN_CONTENT_LENGTH:
            raise ValueError(f"Failed to extract enough content from {url}")

        return ScrapedContent(
            url=url,
            content=content,
        )

    def _validate_url(self, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"Unsupported URL: {url}")

    def _fetch(self, url: str) -> str:
        request = Request(
            url,
            headers={
                "User-Agent": self._USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        try:
            with urlopen(request, timeout=20) as response:
                content_type = response.headers.get("Content-Type", "")
                if not self._is_text_response(content_type):
                    raise ValueError(f"Unsupported content type: {content_type}")

                raw = response.read(self._MAX_BYTES + 1)
                if len(raw) > self._MAX_BYTES:
                    raise ValueError(f"Response too large: {url}")

                charset = response.headers.get_content_charset() or "utf-8"
                return raw.decode(charset, errors="replace")
        except HTTPError as error:
            raise ConnectionError(f"HTTP {error.code} while fetching {url}") from error
        except URLError as error:
            raise ConnectionError(f"Failed to fetch URL: {url}") from error

    def _is_text_response(self, content_type: str) -> bool:
        if not content_type:
            return True
        return any(
            allowed in content_type.lower()
            for allowed in ("text/html", "application/xhtml+xml", "text/plain")
        )

    def _extract_with_trafilatura(self, html: str, url: str) -> str:
        for kwargs in (
            {"favor_precision": True},
            {"favor_recall": True},
        ):
            content = trafilatura.extract(
                html,
                url=url,
                include_comments=False,
                include_tables=True,
                output_format="txt",
                **kwargs,
            )
            if content and len(content.strip()) >= self._MIN_CONTENT_LENGTH:
                return content.strip()
        return ""

    def _extract_visible_text(self, html: str) -> str:
        parser = _VisibleTextParser()
        parser.feed(html)
        return parser.get_text()
