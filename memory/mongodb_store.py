from typing import Any, TypeVar

from pydantic import BaseModel

from schemas.memory_models import (
    ClaimRecord,
    EvidenceNote,
    ResearchRun,
    SourceRecord,
    ToolCallRecord,
    UserMemory,
)

from .base import BaseMemoryStore

T = TypeVar("T", bound=BaseModel)


class MongoMemoryStore(BaseMemoryStore):
    def __init__(self, mongo_uri: str, db_name: str):
        try:
            from pymongo import ASCENDING, MongoClient
        except ImportError as error:
            raise ImportError(
                "pymongo is required for MongoMemoryStore. Install it with "
                "`uv add pymongo` or `pip install pymongo`."
            ) from error

        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self._ascending = ASCENDING
        self._ensure_indexes()

    def create_research_run(self, run: ResearchRun) -> ResearchRun:
        self._upsert("research_runs", run)
        return run

    def update_research_run(self, run: ResearchRun) -> ResearchRun:
        self._upsert("research_runs", run)
        return run

    def get_research_run(self, run_id: str) -> ResearchRun | None:
        doc = self.db.research_runs.find_one({"id": run_id}, {"_id": 0})
        return ResearchRun.model_validate(doc) if doc else None

    def save_source(self, source: SourceRecord) -> SourceRecord:
        self._upsert("source_documents", source)
        return source

    def list_sources(self, run_id: str) -> list[SourceRecord]:
        return self._list_by_run("source_documents", SourceRecord, run_id)

    def save_evidence_note(self, note: EvidenceNote) -> EvidenceNote:
        self._upsert("evidence_notes", note)
        return note

    def list_evidence_notes(self, run_id: str) -> list[EvidenceNote]:
        return self._list_by_run("evidence_notes", EvidenceNote, run_id)

    def save_claim(self, claim: ClaimRecord) -> ClaimRecord:
        self._upsert("claims", claim)
        return claim

    def list_claims(self, run_id: str) -> list[ClaimRecord]:
        return self._list_by_run("claims", ClaimRecord, run_id)

    def save_tool_call(self, tool_call: ToolCallRecord) -> ToolCallRecord:
        self._upsert("tool_calls", tool_call)
        return tool_call

    def list_tool_calls(self, run_id: str) -> list[ToolCallRecord]:
        return self._list_by_run("tool_calls", ToolCallRecord, run_id)

    def save_user_memory(self, memory: UserMemory) -> UserMemory:
        self._upsert("user_memory", memory)
        return memory

    def search_related_memory(
        self,
        query: str,
        *,
        user_id: str | None = None,
        limit: int = 5,
    ) -> list[UserMemory]:
        filter_query: dict[str, Any] = {}
        if user_id is not None:
            filter_query["user_id"] = user_id

        if query.strip():
            filter_query["$text"] = {"$search": query}
            cursor = self.db.user_memory.find(
                filter_query,
                {"_id": 0, "score": {"$meta": "textScore"}},
            ).sort([("score", {"$meta": "textScore"})])
        else:
            cursor = self.db.user_memory.find(filter_query, {"_id": 0}).sort(
                "created_at",
                -1,
            )

        return [UserMemory.model_validate(doc) for doc in cursor.limit(limit)]

    def _ensure_indexes(self) -> None:
        asc = self._ascending
        self.db.research_runs.create_index([("id", asc)], unique=True)
        self.db.research_runs.create_index([("user_id", asc), ("thread_id", asc)])

        for collection_name in (
            "source_documents",
            "evidence_notes",
            "claims",
            "tool_calls",
        ):
            collection = self.db[collection_name]
            collection.create_index([("id", asc)], unique=True)
            collection.create_index([("run_id", asc), ("created_at", asc)])

        self.db.source_documents.create_index([("url", asc)])
        self.db.source_documents.create_index([("content_hash", asc)])
        self.db.evidence_notes.create_index([("source_id", asc)])
        self.db.user_memory.create_index([("id", asc)], unique=True)
        self.db.user_memory.create_index([("user_id", asc), ("namespace", asc)])
        self.db.user_memory.create_index([("content", "text")])

    def _upsert(self, collection_name: str, model: BaseModel) -> None:
        document = model.model_dump(mode="json")
        self.db[collection_name].update_one(
            {"id": document["id"]},
            {"$set": document},
            upsert=True,
        )

    def _list_by_run(
        self,
        collection_name: str,
        model_type: type[T],
        run_id: str,
    ) -> list[T]:
        cursor = self.db[collection_name].find(
            {"run_id": run_id},
            {"_id": 0},
        ).sort("created_at", 1)
        return [model_type.model_validate(doc) for doc in cursor]
