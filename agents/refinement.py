from typing import cast

from langchain.agents import create_agent

from llms import make_llm
from prompts import load_prompt
from schemas import (
    CritiqueResponse,
    RefinementResponse,
    ReportResponse,
    SynthesisResponse,
)


class RefinementAgent:
    def __init__(self):
        self.llm = make_llm(reasoning={"effort": "low"})

    def execute(
        self,
        query: str,
        synthesis: SynthesisResponse,
        draft_report: ReportResponse,
        critique: CritiqueResponse,
    ) -> RefinementResponse:
        refinement_agent = create_agent(
            model=self.llm,
            system_prompt=load_prompt("refinement"),
            response_format=RefinementResponse,
        )

        response = refinement_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"""
                        Original User Query:
                        {query}

                        Synthesized Evidence Map:
                        {synthesis.model_dump_json(indent=2)}

                        Draft Report:
                        {draft_report.model_dump_json(indent=2)}

                        Critique:
                        {critique.model_dump_json(indent=2)}
                        """,
                    )
                ]
            }
        )

        structured_response = cast(dict, response).get("structured_response", response)
        return cast(RefinementResponse, structured_response)
