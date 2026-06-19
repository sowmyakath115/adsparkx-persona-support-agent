from __future__ import annotations

from support_agent.schemas import RetrievedChunk
from support_agent.vector_store import ChromaVectorStore


class Retriever:
    def __init__(self, vector_store: ChromaVectorStore, top_k: int = 4) -> None:
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, query: str) -> list[RetrievedChunk]:
        return self.vector_store.query(query_text=query, top_k=self.top_k)
