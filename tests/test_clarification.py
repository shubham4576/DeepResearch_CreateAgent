from agents.clarification import ClarificationAgent, heuristic_clarification_decision


def test_heuristic_clarification_detects_ambiguous_entity():
    decision = heuristic_clarification_decision("Tell me about Apple")

    assert decision.needs_clarification is True
    assert decision.questions
    assert "apple" in decision.reason.lower()


def test_heuristic_clarification_allows_specific_query():
    decision = heuristic_clarification_decision(
        "Compare Apple Inc revenue growth from 2020 to 2024"
    )

    assert decision.needs_clarification is False
    assert decision.assumed_query == "Compare Apple Inc revenue growth from 2020 to 2024"


def test_clarification_agent_applies_user_answer():
    response = ClarificationAgent().apply_user_answer(
        "Tell me about Apple",
        "I mean Apple Inc, focus on revenue growth since 2020.",
    )

    assert "Apple Inc" in response.clarified_query
    assert "Tell me about Apple" in response.clarified_query
