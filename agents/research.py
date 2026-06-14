from typing import cast

from langchain.agents import create_agent

from llms import make_llm
from prompts import load_prompt
from schemas import ResearchResponse, SourceDocument
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
    
        Title:
        {doc.title}
    
        URL:
        {doc.url}
    
        Content:
        {content}
        """)

    return "\n\n---\n\n".join(sections)


class ResearchAgent:

    def __init__(
        self,
        retrieval_service: RetrievalService,
    ):
        self.retrieval_service = retrieval_service

        self.llm = make_llm(reasoning={"effort": "high"})

    def execute(self, task: str) -> ResearchResponse:

        documents = self.retrieval_service.retrieve(
            query=task,
        )

        system_prompt = load_prompt("research")

        research_agent = create_agent(
            model=self.llm,
            system_prompt=system_prompt,
            response_format=ResearchResponse,
        )

        documents_text = _format_documents(documents)

        response = research_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"""
                                Task:
                                {task}

                                Sources:
                                {documents_text}
                                """,
                    )
                ]
            }
        )

        return cast(ResearchResponse, response)
