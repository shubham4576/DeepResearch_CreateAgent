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
    SCRAPER_PROVIDER: ScraperProvider = ScraperProvider.TRAFILATURA

    SEARCH_MAX_RESULTS: int = 10

    # PATHS
    BASE_PATH: Path = Path(__file__).parent
    PROMPT_PATH: Path = BASE_PATH / "prompts"


@lru_cache
def get_config() -> Config:
    return Config()  # type: ignore


# Load once at startup from environment variables.
config = get_config()  # pyright: ignore[reportCallIssue]
