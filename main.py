from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import cast

from tqdm import tqdm

from agents import create_plan, ResearchAgent
from config import config
from tools import RetrievalService, get_search_provider, get_scraper

output_file = config.BASE_PATH / "output" / "research_plan.txt"

MAX_TASKS = 2


def main():

    query = (
        "Tell me which coffee beans should we use to make best cold"
        "coffee. I live in India."
    )

    print("\nCreating research plan...\n")

    tasks = create_plan(query).tasks
    if MAX_TASKS is not None:
        tasks = tasks[:MAX_TASKS]

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
        max_workers = max(1, min(4, len(tasks)))
        results_by_index = [None] * len(tasks)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(research_agent.execute, task): index
                for index, task in enumerate(tasks)
            }

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                current_task = tasks[index]
                progress.set_postfix(current_task=current_task[:50])

                try:
                    results_by_index[index] = future.result()
                except Exception as error:
                    progress.set_postfix(current_task=f"{current_task[:50]} (failed)")
                    print(f"\nTask {index + 1} failed: {error}")
                finally:
                    progress.update(1)

        results = [
            cast(dict, cast(object, result))["structured_response"]
            for result in results_by_index
            if result is not None
        ]

        # return results

    return results


if __name__ == "__main__":
    response = main()
    print(response[0])
