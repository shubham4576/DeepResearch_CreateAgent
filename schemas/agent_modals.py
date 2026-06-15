from enum import StrEnum

from pydantic import BaseModel, Field


class TaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    NEEDS_FOLLOW_UP = "needs_follow_up"


class ResearchTask(BaseModel):
    id: str = Field(description="Stable task identifier, for example task_001.")
    question: str = Field(description="The concrete research question to answer.")
    objective: str = Field(description="Why this task matters for the report.")
    expected_output: str = Field(
        description="The kind of facts, evidence, and analysis this task should return."
    )
    priority: int = Field(
        default=3,
        ge=1,
        le=5,
        description="1 is highest priority, 5 is lowest priority.",
    )
    dependencies: list[str] = Field(default_factory=list)
    search_queries: list[str] = Field(default_factory=list)
    status: TaskStatus = TaskStatus.PENDING

    def as_query(self) -> str:
        queries = "\n".join(f"- {query}" for query in self.search_queries)
        return (
            f"{self.question}\n\nObjective: {self.objective}\n"
            f"Expected output: {self.expected_output}\n"
            f"Suggested search queries:\n{queries}"
        )


class Plan(BaseModel):
    tasks: list[ResearchTask] = Field(
        default_factory=list,
        description=(
            "Ordered list of research subtasks. Each subtask should be "
            "specific, independently executable, and collectively contribute "
            "to answering the user's query comprehensively."
        ),
    )


class Citation(BaseModel):
    source_id: str
    url: str
    title: str
    excerpt: str | None = None


class ResearchFinding(BaseModel):
    topic: str
    claim: str
    insight: str
    evidence: str
    supporting_source_ids: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    limitations: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)


class ResearchResponse(BaseModel):
    task_id: str
    task: str
    summary: str
    findings: list[ResearchFinding] = Field(default_factory=list)
    sources: list[Citation] = Field(default_factory=list)
    insufficient_evidence: bool = False
    gaps: list[str] = Field(default_factory=list)


class ReflectionResponse(BaseModel):
    task_id: str
    is_complete: bool
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0)
    feedback: str
    missing_topics: list[str] = Field(default_factory=list)
    weak_sources: list[str] = Field(default_factory=list)
    contradictions: list[str] = Field(default_factory=list)
    follow_up_tasks: list[ResearchTask] = Field(default_factory=list)


class SynthesizedClaim(BaseModel):
    claim: str
    supporting_finding_topics: list[str] = Field(default_factory=list)
    supporting_source_ids: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class ReportSection(BaseModel):
    title: str
    purpose: str
    claims: list[SynthesizedClaim] = Field(default_factory=list)


class SynthesisResponse(BaseModel):
    executive_summary: str
    key_themes: list[str] = Field(default_factory=list)
    sections: list[ReportSection] = Field(default_factory=list)
    unresolved_conflicts: list[str] = Field(default_factory=list)
    citation_map: dict[str, list[str]] = Field(default_factory=dict)


class ReportResponse(BaseModel):
    title: str
    markdown: str
    references: list[Citation] = Field(default_factory=list)


class CritiqueResponse(BaseModel):
    factual_accuracy_score: float = Field(default=0.0, ge=0.0, le=1.0)
    citation_coverage_score: float = Field(default=0.0, ge=0.0, le=1.0)
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    unsupported_claims: list[str] = Field(default_factory=list)
    logical_issues: list[str] = Field(default_factory=list)
    missing_sections: list[str] = Field(default_factory=list)
    recommended_improvements: list[str] = Field(default_factory=list)
    requires_revision: bool = True


class RefinementResponse(BaseModel):
    final_report: ReportResponse
    changes_made: list[str] = Field(default_factory=list)
