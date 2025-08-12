from pydantic import BaseModel, Field
from typing import List


class UploadResponse(BaseModel):
    doc_id: str
    summary_bullets: List[str] = Field(default_factory=list)
    num_chunks: int


class AskRequest(BaseModel):
    doc_id: str
    question: str
    top_k: int = 5


class Source(BaseModel):
    page: int
    score: float
    content: str


class AskResponse(BaseModel):
    answer: str
    sources: List[Source] = Field(default_factory=list)