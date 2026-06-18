from memory.context_builder import ContextBuilder, ContextLimits
from schemas import EvidenceNote, ResearchTask, SourceQuality, SourceRecord


def test_context_builder_selects_best_deduped_sources():
    task = ResearchTask(
        id="task_001",
        question="How does Kafka scale?",
        objective="Understand Kafka scalability.",
        expected_output="Evidence-backed explanation.",
    )
    low_quality_duplicate = SourceRecord(
        run_id="run_1",
        url="https://example.com/kafka",
        title="Low Quality",
        content_hash="same",
        content="low quality content",
        quality=SourceQuality(overall_score=0.2),
    )
    high_quality_duplicate = SourceRecord(
        run_id="run_1",
        url="https://example.com/kafka",
        title="High Quality",
        content_hash="same",
        content="high quality content",
        quality=SourceQuality(overall_score=0.9),
    )
    other_source = SourceRecord(
        run_id="run_1",
        url="https://example.com/other",
        title="Other",
        content="other content",
        quality=SourceQuality(overall_score=0.7),
    )

    context = ContextBuilder(
        ContextLimits(max_sources=2, max_chars_per_source=100, max_total_chars=5000)
    ).build_research_context(
        task,
        [low_quality_duplicate, other_source, high_quality_duplicate],
    )

    assert "High Quality" in context
    assert "Other" in context
    assert "Low Quality" not in context


def test_context_builder_caps_source_and_total_context():
    task = ResearchTask(
        id="task_001",
        question="What is a distributed log?",
        objective="Define distributed logs.",
        expected_output="Concise explanation.",
    )
    source = SourceRecord(
        run_id="run_1",
        url="https://example.com/log",
        title="Distributed Log",
        content="x" * 1000,
    )
    note = EvidenceNote(
        run_id="run_1",
        source_id=source.id,
        claim="Distributed logs order records.",
        excerpt="Records are ordered.",
    )

    context = ContextBuilder(
        ContextLimits(max_sources=1, max_chars_per_source=50, max_total_chars=300)
    ).build_research_context(task, [source], [note])

    assert len(context) <= len("\n\n[Context truncated]") + 300
    assert "[Context truncated]" in context
