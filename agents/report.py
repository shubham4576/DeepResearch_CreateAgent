from typing import cast

from langchain.agents import create_agent

from llms import make_llm
from prompts import load_prompt
from schemas import ReportResponse, SynthesisResponse


class ReportGenerationAgent:
    def __init__(self):
        self.llm = make_llm(reasoning={"effort": "low"})

    def execute(self, query: str, synthesis: SynthesisResponse) -> ReportResponse:
        report_agent = create_agent(
            model=self.llm,
            system_prompt=load_prompt("report"),
            response_format=ReportResponse,
        )

        response = report_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"""
                        Original User Query:
                        {query}

                        Synthesized Evidence Map:
                        {synthesis.model_dump_json(indent=2)}
                        """,
                    )
                ]
            }
        )

        structured_response = cast(dict, response).get("structured_response", response)
        return cast(ReportResponse, structured_response)
