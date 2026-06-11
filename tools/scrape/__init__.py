from config import config

from .base import BaseScraper
from .trafilatura_scrapper import TrafilaturaScraper


def get_scraper():

    providers = {
        "trafilatura": TrafilaturaScraper,
    }

    return providers[config.SCRAPER_PROVIDER]()


__all__ = [
    "BaseScraper",
    "get_scraper",
]
