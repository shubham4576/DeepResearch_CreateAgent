from typing import cast

from langchain_core.prompts import ChatPromptTemplate

from llms import make_llm
from prompts import load_prompt
from schemas import ResearchResponse
from tools import get_search_provider, get_scraper

research_llm = make_llm(reasoning={"effort": "high"})

search_provider = get_search_provider()
scraper = get_scraper()


def execute_tasks(tasks: str) -> ResearchResponse:

    system_prompt = load_prompt("research")
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_prompt}"),
            ("human", "{tasks}"),
        ]
    )

    chain = prompt | research_llm.with_structured_output(ResearchResponse)

    response = chain.invoke(
        {
            "system_prompt": system_prompt,
            "tasks": tasks,
        }
    )

    return cast(ResearchResponse, response)
