from schemas import ClarificationDecision
from state import ResearchBudget, ResearchState


def test_research_budget_checks_limits():
    budget = ResearchBudget(
        max_searches=1,
        searches_used=1,
        max_firecrawl_pages=2,
        max_firecrawl_credits=3,
        firecrawl_pages_used=1,
        firecrawl_credits_used=2,
    )

    assert budget.can_search() is False
    assert budget.can_use_firecrawl(estimated_credits=1) is True
    assert budget.can_use_firecrawl(estimated_credits=2) is False


def test_research_state_effective_query_and_serialization():
    state = ResearchState(
        original_query="Tell me about Apple",
        clarification=ClarificationDecision(
            needs_clarification=True,
            reason="Ambiguous entity.",
            questions=["Which Apple do you mean?"],
        ),
    )

    assert state.effective_query == "Tell me about Apple"

    state.clarified_query = "Research Apple Inc revenue growth since 2020."
    dumped = state.model_dump(mode="json")

    assert state.effective_query == "Research Apple Inc revenue growth since 2020."
    assert dumped["clarified_query"] == "Research Apple Inc revenue growth since 2020."
