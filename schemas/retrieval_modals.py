from pydantic import BaseModel


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class SourceDocument(BaseModel):
    title: str
    url: str
    content: str
