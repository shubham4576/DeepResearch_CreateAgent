from config import config

from .base import BaseScraper
from .firecrawl_scraper import FirecrawlScraper
from .general_web_scrapper import GeneralWebScraper
from .hybrid_scraper import HybridScraper
from .newspaper4k_scrapper import Newspaper4kScraper
from .trafilatura_scrapper import TrafilaturaScraper


def get_scraper():

    providers = {
        "firecrawl": FirecrawlScraper,
        "general_web": GeneralWebScraper,
        "hybrid": HybridScraper,
        "newspaper4k": Newspaper4kScraper,
        "trafilatura": TrafilaturaScraper,
    }

    return providers[config.SCRAPER_PROVIDER]()


__all__ = [
    "BaseScraper",
    "get_scraper",
    "FirecrawlScraper",
    "GeneralWebScraper",
    "HybridScraper",
    "Newspaper4kScraper",
    "TrafilaturaScraper",
]
