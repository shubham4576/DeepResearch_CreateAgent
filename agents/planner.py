from typing import cast

from langchain_core.prompts import ChatPromptTemplate

from llms import make_llm
from prompts import load_prompt
from schemas import Plan, ResearchTask, TaskStatus

planner_llm = make_llm(reasoning={"effort": "low"})


def _normalize_plan(plan: Plan) -> Plan:
    normalized_tasks = []

    for index, task in enumerate(plan.tasks, start=1):
        task_id = task.id or f"task_{index:03d}"
        search_queries = task.search_queries or [task.question]

        normalized_tasks.append(
            ResearchTask(
                id=task_id,
                question=task.question,
                objective=task.objective,
                expected_output=task.expected_output,
                priority=task.priority,
                dependencies=task.dependencies,
                search_queries=search_queries,
                status=TaskStatus.PENDING,
            )
        )

    return Plan(tasks=normalized_tasks)


def create_plan(query: str) -> Plan:

    system_prompt = load_prompt("planner")

    prompt = ChatPromptTemplate.from_messages(
        [("system", "{system_prompt}"), ("human", "{query}")]
    )

    chain = prompt | planner_llm.with_structured_output(Plan)
    response = chain.invoke({"system_prompt": system_prompt, "query": query})

    response = cast(Plan, response)

    return _normalize_plan(response)


if __name__ == "__main__":
    _query = "Research Apache Kafka architecture, workflow, scalability, and comparison with RabbitMQ."
    print(create_plan(_query))
