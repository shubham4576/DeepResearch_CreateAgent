from typing import Any

from pydantic import BaseModel, Field

from schemas import (
    ClaimRecord,
    ClarificationDecision,
    CritiqueResponse,
    EvidenceNote,
    Plan,
    ReflectionResponse,
    RefinementResponse,
    ReportResponse,
    ResearchResponse,
    ResearchRun,
    ResearchTask,
    SourceRecord,
    SynthesisResponse,
)


class ResearchBudget(BaseModel):
    max_searches: int = Field(default=12, ge=0)
    max_scrapes: int = Field(default=40, ge=0)
    max_firecrawl_pages: int = Field(default=20, ge=0)
    max_firecrawl_credits: int = Field(default=50, ge=0)
    max_model_calls: int = Field(default=30, ge=0)
    max_follow_up_rounds: int = Field(default=2, ge=0)
    searches_used: int = Field(default=0, ge=0)
    scrapes_used: int = Field(default=0, ge=0)
    firecrawl_pages_used: int = Field(default=0, ge=0)
    firecrawl_credits_used: int = Field(default=0, ge=0)
    model_calls_used: int = Field(default=0, ge=0)
    follow_up_rounds_used: int = Field(default=0, ge=0)

    def can_search(self) -> bool:
        return self.searches_used < self.max_searches

    def can_scrape(self) -> bool:
        return self.scrapes_used < self.max_scrapes

    def can_call_model(self) -> bool:
        return self.model_calls_used < self.max_model_calls

    def can_follow_up(self) -> bool:
        return self.follow_up_rounds_used < self.max_follow_up_rounds

    def can_use_firecrawl(self, estimated_credits: int = 1) -> bool:
        return (
            self.firecrawl_pages_used + 1 <= self.max_firecrawl_pages
            and self.firecrawl_credits_used + estimated_credits
            <= self.max_firecrawl_credits
        )


class ResearchState(BaseModel):
    user_id: str | None = None
    thread_id: str | None = None
    run_id: str | None = None
    original_query: str
    clarified_query: str | None = None
    clarification: ClarificationDecision | None = None
    plan: Plan | None = None
    tasks: list[ResearchTask] = Field(default_factory=list)
    current_task: ResearchTask | None = None
    sources: list[SourceRecord] = Field(default_factory=list)
    evidence_notes: list[EvidenceNote] = Field(default_factory=list)
    claims: list[ClaimRecord] = Field(default_factory=list)
    research_results: list[ResearchResponse] = Field(default_factory=list)
    reflections: list[ReflectionResponse] = Field(default_factory=list)
    synthesis: SynthesisResponse | None = None
    critique: CritiqueResponse | None = None
    refinement: RefinementResponse | None = None
    final_report: ReportResponse | None = None
    run: ResearchRun | None = None
    budget: ResearchBudget = Field(default_factory=ResearchBudget)
    errors: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def effective_query(self) -> str:
        return self.clarified_query or self.original_query
