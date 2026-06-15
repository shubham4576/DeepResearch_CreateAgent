from typing import cast

from langchain.agents import create_agent

from llms import make_llm
from prompts import load_prompt
from schemas import ReflectionResponse, ResearchResponse, SynthesisResponse


class SynthesisAgent:
    def __init__(self):
        self.llm = make_llm(reasoning={"effort": "high"})

    def execute(
        self,
        query: str,
        research_results: list[ResearchResponse],
        reflections: list[ReflectionResponse],
    ) -> SynthesisResponse:
        synthesis_agent = create_agent(
            model=self.llm,
            system_prompt=load_prompt("synthesis"),
            response_format=SynthesisResponse,
        )

        response = synthesis_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"""
                        Original User Query:
                        {query}

                        Validated Research Results:
                        {[result.model_dump() for result in research_results]}

                        Reflection Reviews:
                        {[reflection.model_dump() for reflection in reflections]}
                        """,
                    )
                ]
            }
        )

        structured_response = cast(dict, response).get("structured_response", response)
        return cast(SynthesisResponse, structured_response)
