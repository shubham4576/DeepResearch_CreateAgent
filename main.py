from agents import (
    CritiqueAgent,
    ReflectionAgent,
    RefinementAgent,
    ReportGenerationAgent,
    ResearchAgent,
    SynthesisAgent,
    TaskDistributionAgent,
    create_plan,
) 
from config import config
from schemas import RefinementResponse, ReportResponse, ResearchTask
from tools import RetrievalService, get_scraper, get_search_provider

MAX_TASKS = 2
MAX_RESEARCH_WORKERS = 4


def _build_retrieval_service() -> RetrievalService:
    return RetrievalService(
        search_provider=get_search_provider(),
        scraper=get_scraper(),
    )


def _print_tasks(tasks: list[ResearchTask]) -> None:
    print(f"Generated {len(tasks)} tasks:\n")

    for index, task in enumerate(tasks, start=1):
        print(f"{index}. [{task.id}] {task.question}")
        print(f"   Objective: {task.objective}")
        print(f"   Searches: {', '.join(task.search_queries)}")


def run_research_pipeline(query: str) -> RefinementResponse:
    print("\nCreating research plan...\n")
    plan = create_plan(query)
    tasks = plan.tasks

    if MAX_TASKS is not None:
        tasks = tasks[:MAX_TASKS]

    _print_tasks(tasks)

    retrieval_service = _build_retrieval_service()
    research_agent = ResearchAgent(retrieval_service=retrieval_service)
    distributor = TaskDistributionAgent(
        research_agent=research_agent,
        max_workers=MAX_RESEARCH_WORKERS,
    )

    print("\nStarting parallel research...\n")
    research_results = distributor.execute(tasks)

    print("\nReflecting on research quality...\n")
    reflection_agent = ReflectionAgent()
    reflections = [
        reflection_agent.execute(task=task, research_result=result)
        for task, result in zip(tasks, research_results, strict=False)
    ]

    follow_up_tasks = [
        follow_up_task
        for reflection in reflections
        if not reflection.is_complete
        for follow_up_task in reflection.follow_up_tasks
    ]

    if follow_up_tasks:
        print(f"\nRunning {len(follow_up_tasks)} follow-up research tasks...\n")
        follow_up_results = distributor.execute(follow_up_tasks)
        research_results.extend(follow_up_results)

        reflections.extend(
            reflection_agent.execute(task=task, research_result=result)
            for task, result in zip(follow_up_tasks, follow_up_results, strict=False)
        )

    print("\nSynthesizing evidence...\n")
    synthesis = SynthesisAgent().execute(
        query=query,
        research_results=research_results,
        reflections=reflections,
    )

    print("\nGenerating draft report...\n")
    draft_report = ReportGenerationAgent().execute(query=query, synthesis=synthesis)

    print("\nCritiquing draft report...\n")
    critique = CritiqueAgent().execute(
        query=query,
        synthesis=synthesis,
        draft_report=draft_report,
    )

    print("\nRefining final report...\n")
    if critique.requires_revision:
        refinement = RefinementAgent().execute(
            query=query,
            synthesis=synthesis,
            draft_report=draft_report,
            critique=critique,
        )
    else:
        refinement = RefinementResponse(
            final_report=draft_report,
            changes_made=["Critique did not require revision."],
        )

    return refinement


def main() -> ReportResponse:
    query = (
        "Tell me which coffee beans should we use to make best cold "
        "coffee. I live in India."
    )

    refinement = run_research_pipeline(query)

    output_file = config.BASE_PATH / "output" / "research_report.txt"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(refinement.final_report.markdown, encoding="utf-8")

    return refinement.final_report


if __name__ == "__main__":
    report = main()
    print(report.markdown)
