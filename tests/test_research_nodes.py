from agents import ClarificationAgent, HumanClarifier
from graph import (
    clarify_query_node,
    create_run_node,
    load_related_memory_node,
    resolve_clarification_node,
)
from memory.in_memory_store import InMemoryStore
from schemas import ResearchRunStatus, UserMemory
from state import ResearchState


def test_create_run_and_clarification_nodes():
    store = InMemoryStore()
    state = ResearchState(
        user_id="user_1",
        thread_id="thread_1",
        original_query="Tell me about Apple",
    )

    state = create_run_node(state, store)
    state = clarify_query_node(state, ClarificationAgent(), use_llm=False)

    assert state.run_id is not None
    assert state.run is not None
    assert state.run.status == ResearchRunStatus.NEEDS_CLARIFICATION
    assert state.clarification is not None
    assert state.clarification.needs_clarification is True


def test_resolve_clarification_node_updates_state_and_run():
    store = InMemoryStore()
    state = ResearchState(
        user_id="user_1",
        thread_id="thread_1",
        original_query="Tell me about Apple",
    )
    state = create_run_node(state, store)
    state = clarify_query_node(state, ClarificationAgent(), use_llm=False)

    state = resolve_clarification_node(
        state,
        HumanClarifier(
            ask_user=lambda questions: "Apple Inc, focus on revenue since 2020."
        ),
    )

    assert "Apple Inc" in state.clarified_query
    assert state.run is not None
    assert state.run.status == ResearchRunStatus.RUNNING
    assert state.run.clarified_query == state.clarified_query


def test_load_related_memory_node_adds_memory_to_metadata():
    store = InMemoryStore()
    store.save_user_memory(
        UserMemory(
            user_id="user_1",
            content="Previous research covered Kafka partition replication.",
        )
    )
    state = ResearchState(
        user_id="user_1",
        original_query="Kafka replication details",
    )

    state = load_related_memory_node(state, store)

    assert len(state.metadata["related_memories"]) == 1
    assert "Kafka" in state.metadata["related_memories"][0]["content"]
