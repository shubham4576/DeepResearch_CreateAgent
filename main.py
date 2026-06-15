from tqdm import tqdm

from agents import create_plan, ResearchAgent
from config import config
from tools import RetrievalService, get_search_provider, get_scraper

output_file = config.BASE_PATH / "output" / "research_plan.txt"


def main():

    query = (
        "Tell me which coffee beans should we use to make best cold"
        "coffee. I live in India."
    )

    print("\nCreating research plan...\n")

    tasks = create_plan(query).tasks

    print(f"Generated {len(tasks)} tasks:\n")

    for idx, task in enumerate(tasks, start=1):
        print(f"{idx}. {task}")

    retrieval_service = RetrievalService(
        search_provider=get_search_provider(),
        scraper=get_scraper(),
    )

    research_agent = ResearchAgent(
        retrieval_service=retrieval_service,
    )

    results = []

    print("\nStarting research...\n")

    with tqdm(
        total=len(tasks),
        desc="Research Progress",
        unit="task",
    ) as progress:

        for task in tasks:

            progress.set_postfix(current_task=task[:50])

            result = research_agent.execute(task)

            results.append(result)

            progress.update(1)

    print("\nResearch completed.\n")

    print("=" * 100)
    print("RESEARCH RESULTS")
    print("=" * 100)

    for idx, result in enumerate(results, start=1):

        print(f"\nTask {idx}")
        print("-" * 100)

        print(result)

    return results


if __name__ == "__main__":
    main()
