from typing import cast

from langchain_core.prompts import ChatPromptTemplate

from llms import make_llm
from prompts import load_prompt
from schemas import Plan

planner_llm = make_llm(reasoning={"effort": "xhigh"})


def create_plan(query: str) -> Plan:

    system_prompt = load_prompt("planner")

    prompt = ChatPromptTemplate.from_messages(
        [("system", "{system_prompt}"), ("human", "{query}")]
    )

    chain = prompt | planner_llm.with_structured_output(Plan)
    response = chain.invoke({"system_prompt": system_prompt, "query": query})

    response = cast(Plan, response)

    return response


if __name__ == "__main__":
    _query = "Research Apache Kafka architecture, workflow, scalability, and comparison with RabbitMQ."
    print(create_plan(_query))
