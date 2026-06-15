from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str
    rank: int | None = None
    provider: str | None = None


class RetrievalStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"


class ScrapedContent(BaseModel):
    url: str
    content: str
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SourceDocument(BaseModel):
    id: str
    title: str
    url: str
    domain: str | None = None
    snippet: str | None = None
    rank: int | None = None
    provider: str | None = None
    content: str
    content_length: int = 0
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: RetrievalStatus = RetrievalStatus.SUCCESS
    error: str | None = None
