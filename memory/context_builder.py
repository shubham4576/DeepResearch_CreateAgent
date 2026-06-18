from dataclasses import dataclass

from schemas import (
    ClaimRecord,
    EvidenceNote,
    ResearchResponse,
    ResearchTask,
    SourceRecord,
)


@dataclass(frozen=True)
class ContextLimits:
    max_sources: int = 8
    max_chars_per_source: int = 4000
    max_total_chars: int = 24000


class ContextBuilder:
    def __init__(self, limits: ContextLimits | None = None):
        self.limits = limits or ContextLimits()

    def build_research_context(
        self,
        task: ResearchTask,
        sources: list[SourceRecord],
        evidence_notes: list[EvidenceNote] | None = None,
    ) -> str:
        sections = [
            "Research Task",
            f"Question: {task.question}",
            f"Objective: {task.objective}",
            f"Expected Output: {task.expected_output}",
        ]

        selected_sources = self._select_sources(sources)
        if selected_sources:
            sections.append("Sources")
            for index, source in enumerate(selected_sources, start=1):
                sections.append(self._format_source(index, source))

        selected_notes = self._select_evidence(evidence_notes or [])
        if selected_notes:
            sections.append("Existing Evidence Notes")
            sections.extend(self._format_evidence(note) for note in selected_notes)

        return self._cap_total("\n\n".join(sections))

    def build_synthesis_context(
        self,
        research_results: list[ResearchResponse],
        evidence_notes: list[EvidenceNote],
        claims: list[ClaimRecord],
    ) -> str:
        sections = ["Synthesis Inputs"]

        if claims:
            sections.append("Claims")
            sections.extend(self._format_claim(claim) for claim in claims)

        if evidence_notes:
            sections.append("Evidence Notes")
            sections.extend(
                self._format_evidence(note)
                for note in self._select_evidence(evidence_notes)
            )

        if research_results:
            sections.append("Research Summaries")
            for result in research_results:
                sections.append(
                    "\n".join(
                        [
                            f"Task ID: {result.task_id}",
                            f"Task: {result.task}",
                            f"Summary: {result.summary}",
                            f"Insufficient Evidence: {result.insufficient_evidence}",
                            f"Gaps: {', '.join(result.gaps)}",
                        ]
                    )
                )

        return self._cap_total("\n\n".join(sections))

    def _select_sources(self, sources: list[SourceRecord]) -> list[SourceRecord]:
        deduped: dict[str, SourceRecord] = {}
        for source in sources:
            key = source.content_hash or source.url
            existing = deduped.get(key)
            if existing is None or self._source_score(source) > self._source_score(existing):
                deduped[key] = source

        return sorted(
            deduped.values(),
            key=self._source_score,
            reverse=True,
        )[: self.limits.max_sources]

    def _select_evidence(self, notes: list[EvidenceNote]) -> list[EvidenceNote]:
        return sorted(
            notes,
            key=lambda note: (note.relevance_score + note.credibility_score) / 2,
            reverse=True,
        )[: self.limits.max_sources * 2]

    def _source_score(self, source: SourceRecord) -> float:
        if source.quality:
            return source.quality.overall_score
        if source.rank is not None:
            return max(0.0, 1.0 - ((source.rank - 1) * 0.05))
        return 0.5

    def _format_source(self, index: int, source: SourceRecord) -> str:
        content = (source.content or "").strip()[: self.limits.max_chars_per_source]
        lines = [
            f"Source {index}",
            f"Source ID: {source.id}",
            f"Title: {source.title or 'Untitled'}",
            f"URL: {source.url}",
            f"Domain: {source.domain or 'Unknown'}",
        ]
        if source.snippet:
            lines.append(f"Snippet: {source.snippet}")
        if source.quality:
            lines.append(f"Quality Score: {source.quality.overall_score}")
            if source.quality.reason:
                lines.append(f"Quality Reason: {source.quality.reason}")
        if content:
            lines.append(f"Content:\n{content}")
        return "\n".join(lines)

    def _format_evidence(self, note: EvidenceNote) -> str:
        lines = [
            f"Evidence ID: {note.id}",
            f"Source ID: {note.source_id}",
            f"Claim: {note.claim}",
            f"Excerpt: {note.excerpt}",
            f"Relevance: {note.relevance_score}",
            f"Credibility: {note.credibility_score}",
        ]
        if note.supports:
            lines.append(f"Supports: {', '.join(note.supports)}")
        if note.contradicts:
            lines.append(f"Contradicts: {', '.join(note.contradicts)}")
        if note.limitations:
            lines.append(f"Limitations: {', '.join(note.limitations)}")
        return "\n".join(lines)

    def _format_claim(self, claim: ClaimRecord) -> str:
        lines = [
            f"Claim ID: {claim.id}",
            f"Claim: {claim.claim}",
            f"Confidence: {claim.confidence}",
            f"Status: {claim.status}",
        ]
        if claim.supporting_evidence_ids:
            lines.append(
                f"Supporting Evidence: {', '.join(claim.supporting_evidence_ids)}"
            )
        if claim.contradicting_evidence_ids:
            lines.append(
                f"Contradicting Evidence: {', '.join(claim.contradicting_evidence_ids)}"
            )
        if claim.reason:
            lines.append(f"Reason: {claim.reason}")
        return "\n".join(lines)

    def _cap_total(self, text: str) -> str:
        if len(text) <= self.limits.max_total_chars:
            return text
        return text[: self.limits.max_total_chars].rstrip() + "\n\n[Context truncated]"
