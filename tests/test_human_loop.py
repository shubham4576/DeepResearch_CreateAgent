from agents.human_loop import HumanClarifier
from schemas import ClarificationDecision


def test_human_clarifier_returns_assumed_query_when_clear():
    response = HumanClarifier().resolve(
        "Compare Kafka and RabbitMQ",
        ClarificationDecision(
            needs_clarification=False,
            reason="Clear enough.",
            assumed_query="Compare Kafka and RabbitMQ for event streaming.",
        ),
    )

    assert response.clarified_query == "Compare Kafka and RabbitMQ for event streaming."


def test_human_clarifier_uses_callback_answer():
    clarifier = HumanClarifier(
        ask_user=lambda questions: "Apple Inc, business performance since 2020."
    )

    response = clarifier.resolve(
        "Tell me about Apple",
        ClarificationDecision(
            needs_clarification=True,
            reason="Ambiguous entity.",
            questions=["Which Apple do you mean?"],
        ),
    )

    assert "Apple Inc" in response.clarified_query
    assert "Tell me about Apple" in response.clarified_query
