from abc import ABC, abstractmethod

from schemas.memory_models import (
    ClaimRecord,
    EvidenceNote,
    ResearchRun,
    SourceRecord,
    ToolCallRecord,
    UserMemory,
)


class BaseMemoryStore(ABC):
    @abstractmethod
    def create_research_run(self, run: ResearchRun) -> ResearchRun:
        pass

    @abstractmethod
    def update_research_run(self, run: ResearchRun) -> ResearchRun:
        pass

    @abstractmethod
    def get_research_run(self, run_id: str) -> ResearchRun | None:
        pass

    @abstractmethod
    def save_source(self, source: SourceRecord) -> SourceRecord:
        pass

    @abstractmethod
    def list_sources(self, run_id: str) -> list[SourceRecord]:
        pass

    @abstractmethod
    def save_evidence_note(self, note: EvidenceNote) -> EvidenceNote:
        pass

    @abstractmethod
    def list_evidence_notes(self, run_id: str) -> list[EvidenceNote]:
        pass

    @abstractmethod
    def save_claim(self, claim: ClaimRecord) -> ClaimRecord:
        pass

    @abstractmethod
    def list_claims(self, run_id: str) -> list[ClaimRecord]:
        pass

    @abstractmethod
    def save_tool_call(self, tool_call: ToolCallRecord) -> ToolCallRecord:
        pass

    @abstractmethod
    def list_tool_calls(self, run_id: str) -> list[ToolCallRecord]:
        pass

    @abstractmethod
    def save_user_memory(self, memory: UserMemory) -> UserMemory:
        pass

    @abstractmethod
    def search_related_memory(
        self,
        query: str,
        *,
        user_id: str | None = None,
        limit: int = 5,
    ) -> list[UserMemory]:
        pass
