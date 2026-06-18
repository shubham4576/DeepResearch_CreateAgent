import pytest

from tools.scrape.general_web_scrapper import GeneralWebScraper


def test_general_web_scraper_falls_back_to_visible_text(monkeypatch):
    html = """
    <html>
      <head>
        <title>Product Docs</title>
        <style>.hidden { display: none; }</style>
        <script>window.secret = "ignore me";</script>
      </head>
      <body>
        <nav>Docs Home Pricing Changelog</nav>
        <main>
          <h1>Kafka Connect Configuration</h1>
          <p>
            Kafka Connect runs source and sink connectors. Workers coordinate
            connector tasks, store offsets, and expose a REST API for managing
            connector lifecycle across distributed deployments.
          </p>
          <p>
            Production deployments should configure replication factors,
            plugin paths, converter settings, and status storage topics before
            starting workloads.
          </p>
        </main>
      </body>
    </html>
    """
    scraper = GeneralWebScraper()

    monkeypatch.setattr(scraper, "_fetch", lambda url: html)
    monkeypatch.setattr(scraper, "_extract_with_trafilatura", lambda html, url: "")

    scraped = scraper.scrape("https://example.com/docs/kafka-connect")

    assert "Kafka Connect Configuration" in scraped.content
    assert "Workers coordinate connector tasks" in scraped.content
    assert "ignore me" not in scraped.content


def test_general_web_scraper_rejects_non_http_urls():
    scraper = GeneralWebScraper()

    with pytest.raises(ValueError, match="Unsupported URL"):
        scraper.scrape("file:///etc/passwd")
