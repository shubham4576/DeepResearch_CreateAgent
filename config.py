import warnings

warnings.filterwarnings("ignore", message="Pydantic serializer warnings")

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from enum import StrEnum
from functools import lru_cache


class SearchProvider(StrEnum):
    DUCKDUCKGO = "duckduckgo"


class ScraperProvider(StrEnum):
    FIRECRAWL = "firecrawl"
    GENERAL_WEB = "general_web"
    HYBRID = "hybrid"
    NEWSPAPER4K = "newspaper4k"
    TRAFILATURA = "trafilatura"


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )

    OPENAI_API_KEY: SecretStr
    OPENAI_DEFAULT_MODEL: str

    SEARCH_PROVIDER: SearchProvider = SearchProvider.DUCKDUCKGO
    SCRAPER_PROVIDER: ScraperProvider = ScraperProvider.GENERAL_WEB

    SEARCH_MAX_RESULTS: int = 10

    # PATHS
    BASE_PATH: Path = Path(__file__).parent
    PROMPT_PATH: Path = BASE_PATH / "prompts"

    # DATABASE FOR LONG TERM MEMORY AND STORING ALL THE EVIDENCE
    MONGO_URI: str | None = None
    MONGO_DB_NAME: str = "deep_research"

    # FIRECRAWL SCRAPPER DETAILS (PAID SERVICE) USING FREE TIER
    FIRECRAWL_API_KEY: SecretStr | None = None
    FIRECRAWL_ENABLED: bool = False
    FIRECRAWL_MAX_PAGES_PER_RUN: int = 20
    FIRECRAWL_MAX_CREDITS_PER_RUN: int = 50

    # CONTEXT CONTROL
    CONTEXT_MAX_CHARS_PER_SOURCE: int = 4000
    CONTEXT_MAX_SOURCES: int = 8


@lru_cache
def get_config() -> Config:
    return Config()  # type: ignore


# Load once at startup from environment variables.
config = get_config()  # pyright: ignore[reportCallIssue]
