from typing import cast

from langchain_core.prompts import ChatPromptTemplate

from llms import make_llm
from prompts import load_prompt
from schemas import ClarificationDecision, ClarificationResponse


AMBIGUOUS_ENTITY_TERMS = {
    "apple",
    "amazon",
    "jaguar",
    "mercury",
    "python",
    "java",
    "go",
    "rust",
    "swift",
    "delta",
    "oracle",
    "tesla",
}

VAGUE_RESEARCH_PREFIXES = (
    "tell me about ",
    "research ",
    "explain ",
    "what about ",
    "deep dive on ",
)


def heuristic_clarification_decision(query: str) -> ClarificationDecision:
    normalized = " ".join(query.lower().strip().split())
    tokens = set(normalized.replace("?", "").split())

    if not normalized:
        return ClarificationDecision(
            needs_clarification=True,
            reason="The query is empty.",
            questions=["What topic should the research focus on?"],
        )

    ambiguous_terms = sorted(tokens & AMBIGUOUS_ENTITY_TERMS)
    starts_vague = normalized.startswith(VAGUE_RESEARCH_PREFIXES)
    is_short = len(tokens) <= 4

    if ambiguous_terms and (starts_vague or is_short):
        term = ambiguous_terms[0]
        return ClarificationDecision(
            needs_clarification=True,
            reason=f"'{term}' can refer to multiple subjects.",
            questions=[
                f"Which '{term}' do you mean?",
                "What angle should the research focus on: overview, technical details, market/business, history, or comparison?",
            ],
        )

    if starts_vague and is_short:
        return ClarificationDecision(
            needs_clarification=True,
            reason="The query gives a broad topic but not the desired research angle.",
            questions=[
                "What specific angle should the research focus on?",
                "Who is the intended audience: beginner, technical, business, or academic?",
            ],
        )

    return ClarificationDecision(
        needs_clarification=False,
        reason="The query is specific enough to plan.",
        assumed_query=query.strip(),
    )


class ClarificationAgent:
    def __init__(self):
        self.llm = make_llm(reasoning={"effort": "low"})

    def decide(self, query: str, *, use_llm: bool = True) -> ClarificationDecision:
        heuristic_decision = heuristic_clarification_decision(query)
        if heuristic_decision.needs_clarification or not use_llm:
            return heuristic_decision

        prompt = ChatPromptTemplate.from_messages(
            [("system", "{system_prompt}"), ("human", "{query}")]
        )
        chain = prompt | self.llm.with_structured_output(ClarificationDecision)
        response = chain.invoke(
            {
                "system_prompt": load_prompt("clarification"),
                "query": query,
            }
        )
        decision = cast(ClarificationDecision, response)

        if not decision.needs_clarification and not decision.assumed_query:
            decision.assumed_query = query.strip()

        return decision

    def apply_user_answer(
        self,
        original_query: str,
        user_answer: str,
        assumptions: list[str] | None = None,
    ) -> ClarificationResponse:
        answer = user_answer.strip()
        if not answer:
            return ClarificationResponse(
                clarified_query=original_query.strip(),
                assumptions=assumptions or ["Proceeding with the original query."],
            )

        return ClarificationResponse(
            clarified_query=f"{original_query.strip()}\n\nClarification: {answer}",
            assumptions=assumptions or [],
        )
