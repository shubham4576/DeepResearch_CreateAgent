from collections.abc import Callable

from schemas import ClarificationDecision, ClarificationResponse


AskUser = Callable[[list[str]], str]


class HumanClarifier:
    def __init__(self, ask_user: AskUser | None = None):
        self.ask_user = ask_user or self._ask_user_cli

    def resolve(
        self,
        original_query: str,
        decision: ClarificationDecision,
    ) -> ClarificationResponse:
        if not decision.needs_clarification:
            return ClarificationResponse(
                clarified_query=decision.assumed_query or original_query.strip(),
                assumptions=[],
            )

        answer = self.ask_user(decision.questions).strip()
        if not answer:
            return ClarificationResponse(
                clarified_query=decision.assumed_query or original_query.strip(),
                assumptions=[
                    "User did not provide clarification; proceeding with available query."
                ],
            )

        return ClarificationResponse(
            clarified_query=f"{original_query.strip()}\n\nClarification: {answer}",
            assumptions=[],
        )

    def _ask_user_cli(self, questions: list[str]) -> str:
        print("\nClarification needed:\n")
        for index, question in enumerate(questions, start=1):
            print(f"{index}. {question}")
        return input("\nYour clarification: ")
