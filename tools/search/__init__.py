from config import config

from .base import BaseSearchProvider
from .duckduckgo import DuckDuckGoSearchProvider


def get_search_provider() -> BaseSearchProvider:
    providers = {
        "duckduckgo": DuckDuckGoSearchProvider,
    }

    return providers[config.SEARCH_PROVIDER]()


__all__ = [
    "BaseSearchProvider",
    "get_search_provider",
]
