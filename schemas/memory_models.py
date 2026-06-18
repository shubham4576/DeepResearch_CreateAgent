from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def _new_id() -> str:
    return str(uuid4())


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ResearchRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    NEEDS_CLARIFICATION = "needs_clarification"
    COMPLETED = "completed"
    FAILED = "failed"


class MemoryType(StrEnum):
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"
    USER_PREFERENCE = "user_preference"
    RESEARCH_SUMMARY = "research_summary"


class ToolCallStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class ResearchRun(BaseModel):
    id: str = Field(default_factory=_new_id)
    user_id: str | None = None
    thread_id: str | None = None
    original_query: str
    clarified_query: str | None = None
    status: ResearchRunStatus = ResearchRunStatus.PENDING
    final_report_id: str | None = None
    summary: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
    completed_at: datetime | None = None


class SourceQuality(BaseModel):
    is_primary_source: bool = False
    authority_score: float = Field(default=0.5, ge=0.0, le=1.0)
    freshness_score: float = Field(default=0.5, ge=0.0, le=1.0)
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    spam_score: float = Field(default=0.0, ge=0.0, le=1.0)
    overall_score: float = Field(default=0.5, ge=0.0, le=1.0)
    reason: str | None = None


class SourceRecord(BaseModel):
    id: str = Field(default_factory=_new_id)
    run_id: str
    url: str
    title: str | None = None
    domain: str | None = None
    snippet: str | None = None
    content: str | None = None
    content_hash: str | None = None
    scraper_provider: str | None = None
    search_provider: str | None = None
    rank: int | None = None
    quality: SourceQuality | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    fetched_at: datetime = Field(default_factory=_now)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class EvidenceNote(BaseModel):
    id: str = Field(default_factory=_new_id)
    run_id: str
    source_id: str
    claim: str
    excerpt: str
    topic: str | None = None
    relevance_score: float = Field(default=0.5, ge=0.0, le=1.0)
    credibility_score: float = Field(default=0.5, ge=0.0, le=1.0)
    supports: list[str] = Field(default_factory=list)
    contradicts: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class ClaimRecord(BaseModel):
    id: str = Field(default_factory=_new_id)
    run_id: str
    claim: str
    status: str = "draft"
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    reason: str | None = None
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class ToolCallRecord(BaseModel):
    id: str = Field(default_factory=_new_id)
    run_id: str
    tool_name: str
    input: dict[str, Any] = Field(default_factory=dict)
    output_summary: str | None = None
    status: ToolCallStatus = ToolCallStatus.SUCCESS
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    started_at: datetime = Field(default_factory=_now)
    completed_at: datetime | None = None


class ConversationThread(BaseModel):
    id: str = Field(default_factory=_new_id)
    user_id: str | None = None
    title: str | None = None
    summary: str | None = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class UserMemory(BaseModel):
    id: str = Field(default_factory=_new_id)
    user_id: str
    memory_type: MemoryType = MemoryType.SEMANTIC
    content: str
    namespace: str = "default"
    source_run_id: str | None = None
    embedding: list[float] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
