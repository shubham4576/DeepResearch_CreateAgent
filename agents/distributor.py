from concurrent.futures import ThreadPoolExecutor, as_completed

from schemas import ResearchResponse, ResearchTask

from .research import ResearchAgent


class TaskDistributionAgent:
    def __init__(self, research_agent: ResearchAgent, max_workers: int = 4):
        self.research_agent = research_agent
        self.max_workers = max_workers

    def execute(self, tasks: list[ResearchTask]) -> list[ResearchResponse]:
        if not tasks:
            return []

        worker_count = max(1, min(self.max_workers, len(tasks)))
        results_by_index: list[ResearchResponse | None] = [None] * len(tasks)

        with ThreadPoolExecutor(max_workers=worker_count) as executor:
            future_to_index = {
                executor.submit(self.research_agent.execute, task): index
                for index, task in enumerate(tasks)
            }

            for future in as_completed(future_to_index):
                index = future_to_index[future]
                task = tasks[index]

                try:
                    results_by_index[index] = future.result()
                except Exception as error:
                    results_by_index[index] = ResearchResponse(
                        task_id=task.id,
                        task=task.question,
                        summary="Research task failed before producing findings.",
                        insufficient_evidence=True,
                        gaps=["Task execution failed."],
                        error=str(error),
                    )

        return [result for result in results_by_index if result is not None]
