from urllib.parse import urlparse

from memory import BaseMemoryStore, log_tool_call
from schemas import (
    EvidenceNote,
    SearchResult,
    SourceDocument,
    SourceRecord,
    ToolCallStatus,
)

from .service import RetrievalService


class RetrievalTools:
    def __init__(
        self,
        retrieval_service: RetrievalService,
        memory_store: BaseMemoryStore,
        run_id: str,
    ):
        self.retrieval_service = retrieval_service
        self.memory_store = memory_store
        self.run_id = run_id

    def search_web(self, query: str, max_results: int = 10) -> list[SearchResult]:
        try:
            results = self.retrieval_service.search(query, max_results)
            log_tool_call(
                self.memory_store,
                run_id=self.run_id,
                tool_name="search_web",
                input={"query": query, "max_results": max_results},
                output_summary=f"{len(results)} results",
            )
            return results
        except Exception as error:
            log_tool_call(
                self.memory_store,
                run_id=self.run_id,
                tool_name="search_web",
                input={"query": query, "max_results": max_results},
                status=ToolCallStatus.FAILED,
                error=str(error),
            )
            raise

    def scrape_url(
        self,
        url: str,
        *,
        title: str | None = None,
        snippet: str | None = None,
        rank: int | None = None,
        provider: str | None = None,
    ) -> SourceDocument | None:
        result = SearchResult(
            title=title or url,
            url=url,
            snippet=snippet or "",
            rank=rank,
            provider=provider,
        )
        try:
            document = self.retrieval_service.scrape(result)
            if document:
                self.memory_store.save_source(self._source_record_from_document(document))
            log_tool_call(
                self.memory_store,
                run_id=self.run_id,
                tool_name="scrape_url",
                input={"url": url},
                output_summary="1 document" if document else "no document",
            )
            return document
        except Exception as error:
            log_tool_call(
                self.memory_store,
                run_id=self.run_id,
                tool_name="scrape_url",
                input={"url": url},
                status=ToolCallStatus.FAILED,
                error=str(error),
            )
            raise

    def retrieve_web(self, query: str, max_results: int = 10) -> list[SourceDocument]:
        try:
            documents = self.retrieval_service.retrieve(query, max_results)
            for document in documents:
                self.memory_store.save_source(self._source_record_from_document(document))
            log_tool_call(
                self.memory_store,
                run_id=self.run_id,
                tool_name="retrieve_web",
                input={"query": query, "max_results": max_results},
                output_summary=f"{len(documents)} documents",
            )
            return documents
        except Exception as error:
            log_tool_call(
                self.memory_store,
                run_id=self.run_id,
                tool_name="retrieve_web",
                input={"query": query, "max_results": max_results},
                status=ToolCallStatus.FAILED,
                error=str(error),
            )
            raise

    def save_evidence(self, note: EvidenceNote) -> EvidenceNote:
        saved = self.memory_store.save_evidence_note(note)
        log_tool_call(
            self.memory_store,
            run_id=self.run_id,
            tool_name="save_evidence",
            input={"evidence_id": saved.id, "source_id": saved.source_id},
            output_summary="evidence saved",
        )
        return saved

    def read_source(self, source_id: str) -> SourceRecord | None:
        sources = self.memory_store.list_sources(self.run_id)
        source = next((item for item in sources if item.id == source_id), None)
        log_tool_call(
            self.memory_store,
            run_id=self.run_id,
            tool_name="read_source",
            input={"source_id": source_id},
            output_summary="source found" if source else "source missing",
        )
        return source

    def search_memory(self, query: str, user_id: str | None = None, limit: int = 5):
        results = self.memory_store.search_related_memory(
            query,
            user_id=user_id,
            limit=limit,
        )
        log_tool_call(
            self.memory_store,
            run_id=self.run_id,
            tool_name="search_memory",
            input={"query": query, "user_id": user_id, "limit": limit},
            output_summary=f"{len(results)} memories",
        )
        return results

    def _source_record_from_document(self, document: SourceDocument) -> SourceRecord:
        return SourceRecord(
            id=document.id,
            run_id=self.run_id,
            url=document.url,
            title=document.title,
            domain=document.domain or urlparse(document.url).netloc,
            snippet=document.snippet,
            content=document.content,
            search_provider=document.provider,
            rank=document.rank,
            fetched_at=document.fetched_at,
        )
