from typing import cast

from langchain.agents import create_agent

from config import config
from llms import make_llm
from prompts import load_prompt
from schemas import Citation, ResearchResponse, ResearchTask, SourceDocument
from tools import RetrievalService


def _format_documents(
    documents: list[SourceDocument],
    max_chars_per_doc: int = 4000,
) -> str:
    sections = []

    for i, doc in enumerate(documents, start=1):
        content = doc.content[:max_chars_per_doc]

        sections.append(f"""
        Source {i}

        Source ID:
        {doc.id}
    
        Title:
        {doc.title}
    
        URL:
        {doc.url}

        Domain:
        {doc.domain}

        Search Snippet:
        {doc.snippet}
    
        Content:
        {content}
        """)

    return "\n\n---\n\n".join(sections)


def _research_user_payload(task: ResearchTask, documents_text: str) -> str:
    return f"""
                                Task ID:
                                {task.id}

                                Research Question:
                                {task.question}

                                Objective:
                                {task.objective}

                                Expected Output:
                                {task.expected_output}

                                Sources:
                                {documents_text}
                                """


def _safe_debug_filename(task_id: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in task_id)
    return f"research_context_{safe or 'task'}.md"


class ResearchAgent:

    def __init__(
        self,
        retrieval_service: RetrievalService,
    ):
        self.retrieval_service = retrieval_service

        self.llm = make_llm(reasoning={"effort": "low"})

    def _retrieve_documents(self, task: ResearchTask) -> list[SourceDocument]:
        queries = task.search_queries or [task.question]
        documents_by_id: dict[str, SourceDocument] = {}

        for query in queries:
            for document in self.retrieval_service.retrieve(query=query):
                documents_by_id[document.id] = document

        return list(documents_by_id.values())

    def execute(self, task: ResearchTask | str) -> ResearchResponse:
        if isinstance(task, str):
            task = ResearchTask(
                id="task_001",
                question=task,
                objective=task,
                expected_output="Evidence-backed findings for the task.",
                search_queries=[task],
            )

        documents = self._retrieve_documents(task)

        system_prompt = load_prompt("research")

        research_agent = create_agent(
            model=self.llm,
            system_prompt=system_prompt,
            response_format=ResearchResponse,
        )

        documents_text = _format_documents(documents)
        user_payload = _research_user_payload(task, documents_text)
        self._write_debug_context(
            task=task,
            documents=documents,
            system_prompt=system_prompt,
            user_payload=user_payload,
        )

        response = research_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        user_payload,
                    )
                ]
            }
        )

        structured_response = cast(dict, response).get("structured_response", response)
        research_response = cast(ResearchResponse, structured_response)

        if not research_response.sources:
            research_response.sources = [
                Citation(
                    source_id=document.id,
                    url=document.url,
                    title=document.title,
                    excerpt=document.snippet,
                )
                for document in documents
            ]

        return research_response

    def _write_debug_context(
        self,
        *,
        task: ResearchTask,
        documents: list[SourceDocument],
        system_prompt: str,
        user_payload: str,
    ) -> None:
        if not config.DEBUG_RESEARCH_CONTEXT:
            return

        config.DEBUG_OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
        output_file = config.DEBUG_OUTPUT_PATH / _safe_debug_filename(task.id)
        source_summary = "\n".join(
            f"- {document.title} | {document.url} | {document.content_length} chars"
            for document in documents
        )
        output_file.write_text(
            "\n".join(
                [
                    f"# Research Context Debug: {task.id}",
                    "",
                    "## Source Summary",
                    "",
                    source_summary or "No source documents retrieved.",
                    "",
                    "## System Prompt",
                    "",
                    "```text",
                    system_prompt,
                    "```",
                    "",
                    "## User Payload Sent To Research Agent",
                    "",
                    "```text",
                    user_payload,
                    "```",
                    "",
                ]
            ),
            encoding="utf-8",
        )
