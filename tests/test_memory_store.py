from memory.in_memory_store import InMemoryStore
from schemas import (
    ClaimRecord,
    EvidenceNote,
    ResearchRun,
    SourceRecord,
    ToolCallRecord,
    UserMemory,
)


def test_in_memory_store_persists_research_artifacts():
    store = InMemoryStore()
    run = store.create_research_run(
        ResearchRun(
            user_id="user_1",
            thread_id="thread_1",
            original_query="Research Kafka architecture",
        )
    )

    source = store.save_source(
        SourceRecord(
            run_id=run.id,
            url="https://example.com/kafka",
            title="Kafka Architecture",
            content="Kafka uses topics, partitions, brokers, and replication.",
        )
    )
    evidence = store.save_evidence_note(
        EvidenceNote(
            run_id=run.id,
            source_id=source.id,
            claim="Kafka distributes data across partitions.",
            excerpt="Kafka uses topics, partitions, brokers, and replication.",
        )
    )
    claim = store.save_claim(
        ClaimRecord(
            run_id=run.id,
            claim="Kafka uses partitions for horizontal scalability.",
            supporting_evidence_ids=[evidence.id],
            confidence=0.8,
        )
    )
    tool_call = store.save_tool_call(
        ToolCallRecord(
            run_id=run.id,
            tool_name="search_web",
            input={"query": "Kafka architecture"},
            output_summary="1 result",
        )
    )

    assert store.get_research_run(run.id) == run
    assert store.list_sources(run.id) == [source]
    assert store.list_evidence_notes(run.id) == [evidence]
    assert store.list_claims(run.id) == [claim]
    assert store.list_tool_calls(run.id) == [tool_call]


def test_in_memory_store_searches_related_user_memory():
    store = InMemoryStore()
    matching = store.save_user_memory(
        UserMemory(
            user_id="user_1",
            content="The user previously researched Kafka broker replication.",
        )
    )
    store.save_user_memory(
        UserMemory(
            user_id="user_2",
            content="The user prefers short answers about React.",
        )
    )

    results = store.search_related_memory(
        "Kafka replication",
        user_id="user_1",
    )

    assert results == [matching]
