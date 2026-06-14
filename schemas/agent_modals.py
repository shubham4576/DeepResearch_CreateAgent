from typing import List

from pydantic import BaseModel, Field


class Plan(BaseModel):
    tasks: List[str] = Field(
        "...",
        description=(
            "Ordered list of research subtasks. Each subtask should be "
            "specific, independently executable, and collectively contribute "
            "to answering the user's query comprehensively."
        ),
    )


class ResearchFinding(BaseModel):
    topic: str
    insight: str
    evidence: str


class ResearchResponse(BaseModel):
    task: str
    summary: str
    findings: list[ResearchFinding]
    sources: list[str]


class ReflectionResponse(BaseModel):
    is_complete: bool
    feedback: str
    missing_topics: list[str]


class ScrapedContent(BaseModel):
    url: str
    content: str
