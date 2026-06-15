from typing import cast

from langchain.agents import create_agent

from llms import make_llm
from prompts import load_prompt
from schemas import ReflectionResponse, ResearchResponse, ResearchTask


class ReflectionAgent:
    def __init__(self):
        self.llm = make_llm(reasoning={"effort": "high"})

    def execute(
        self,
        task: ResearchTask,
        research_result: ResearchResponse,
    ) -> ReflectionResponse:
        reflection_agent = create_agent(
            model=self.llm,
            system_prompt=load_prompt("reflection"),
            response_format=ReflectionResponse,
        )

        response = reflection_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"""
                        Original Task:
                        {task.model_dump_json(indent=2)}

                        Research Result:
                        {research_result.model_dump_json(indent=2)}
                        """,
                    )
                ]
            }
        )

        structured_response = cast(dict, response).get("structured_response", response)
        return cast(ReflectionResponse, structured_response)
