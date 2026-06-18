from collections import defaultdict

from schemas.memory_models import (
    ClaimRecord,
    EvidenceNote,
    ResearchRun,
    SourceRecord,
    ToolCallRecord,
    UserMemory,
)

from .base import BaseMemoryStore


class InMemoryStore(BaseMemoryStore):
    def __init__(self):
        self._runs: dict[str, ResearchRun] = {}
        self._sources_by_run: dict[str, list[SourceRecord]] = defaultdict(list)
        self._evidence_by_run: dict[str, list[EvidenceNote]] = defaultdict(list)
        self._claims_by_run: dict[str, list[ClaimRecord]] = defaultdict(list)
        self._tool_calls_by_run: dict[str, list[ToolCallRecord]] = defaultdict(list)
        self._user_memories: list[UserMemory] = []

    def create_research_run(self, run: ResearchRun) -> ResearchRun:
        self._runs[run.id] = run
        return run

    def update_research_run(self, run: ResearchRun) -> ResearchRun:
        self._runs[run.id] = run
        return run

    def get_research_run(self, run_id: str) -> ResearchRun | None:
        return self._runs.get(run_id)

    def save_source(self, source: SourceRecord) -> SourceRecord:
        self._upsert(self._sources_by_run[source.run_id], source)
        return source

    def list_sources(self, run_id: str) -> list[SourceRecord]:
        return list(self._sources_by_run.get(run_id, []))

    def save_evidence_note(self, note: EvidenceNote) -> EvidenceNote:
        self._upsert(self._evidence_by_run[note.run_id], note)
        return note

    def list_evidence_notes(self, run_id: str) -> list[EvidenceNote]:
        return list(self._evidence_by_run.get(run_id, []))

    def save_claim(self, claim: ClaimRecord) -> ClaimRecord:
        self._upsert(self._claims_by_run[claim.run_id], claim)
        return claim

    def list_claims(self, run_id: str) -> list[ClaimRecord]:
        return list(self._claims_by_run.get(run_id, []))

    def save_tool_call(self, tool_call: ToolCallRecord) -> ToolCallRecord:
        self._upsert(self._tool_calls_by_run[tool_call.run_id], tool_call)
        return tool_call

    def list_tool_calls(self, run_id: str) -> list[ToolCallRecord]:
        return list(self._tool_calls_by_run.get(run_id, []))

    def save_user_memory(self, memory: UserMemory) -> UserMemory:
        self._upsert(self._user_memories, memory)
        return memory

    def search_related_memory(
        self,
        query: str,
        *,
        user_id: str | None = None,
        limit: int = 5,
    ) -> list[UserMemory]:
        terms = {term.lower() for term in query.split() if term.strip()}
        scored: list[tuple[int, UserMemory]] = []

        for memory in self._user_memories:
            if user_id is not None and memory.user_id != user_id:
                continue

            content_terms = set(memory.content.lower().split())
            score = len(terms & content_terms)
            if score:
                scored.append((score, memory))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [memory for _, memory in scored[:limit]]

    def _upsert(self, items: list, item) -> None:
        for index, existing in enumerate(items):
            if existing.id == item.id:
                items[index] = item
                return
        items.append(item)
