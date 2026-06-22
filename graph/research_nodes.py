from agents.clarification import ClarificationAgent
from agents.human_loop import HumanClarifier
from memory import BaseMemoryStore
from schemas import ResearchRun, ResearchRunStatus
from state import ResearchState


def create_run_node(
    state: ResearchState,
    memory_store: BaseMemoryStore,
) -> ResearchState:
    if state.run_id:
        return state

    run = ResearchRun(
        user_id=state.user_id,
        thread_id=state.thread_id,
        original_query=state.original_query,
        status=ResearchRunStatus.RUNNING,
    )
    memory_store.create_research_run(run)
    state.run = run
    state.run_id = run.id
    return state


def clarify_query_node(
    state: ResearchState,
    clarification_agent: ClarificationAgent,
    *,
    use_llm: bool = True,
) -> ResearchState:
    decision = clarification_agent.decide(state.original_query, use_llm=use_llm)
    state.clarification = decision

    if not decision.needs_clarification:
        state.clarified_query = decision.assumed_query or state.original_query
    elif state.run:
        state.run.status = ResearchRunStatus.NEEDS_CLARIFICATION

    return state


def resolve_clarification_node(
    state: ResearchState,
    human_clarifier: HumanClarifier,
) -> ResearchState:
    if not state.clarification:
        return state

    response = human_clarifier.resolve(
        state.original_query,
        state.clarification,
    )
    state.clarified_query = response.clarified_query
    state.metadata["clarification_assumptions"] = response.assumptions

    if state.run:
        state.run.clarified_query = response.clarified_query
        state.run.status = ResearchRunStatus.RUNNING

    return state


def load_related_memory_node(
    state: ResearchState,
    memory_store: BaseMemoryStore,
    *,
    limit: int = 5,
) -> ResearchState:
    if not state.user_id:
        state.metadata["related_memories"] = []
        return state

    memories = memory_store.search_related_memory(
        state.effective_query,
        user_id=state.user_id,
        limit=limit,
    )
    state.metadata["related_memories"] = [
        memory.model_dump(mode="json") for memory in memories
    ]
    return state
