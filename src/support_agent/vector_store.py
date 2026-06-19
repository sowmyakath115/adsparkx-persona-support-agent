from __future__ import annotations

from pathlib import Path
from typing import Any

from support_agent.embeddings import EmbeddingProvider
from support_agent.schemas import DocumentChunk, RetrievedChunk, SourceLocation


class ChromaVectorStore:
    def __init__(self, path: Path, collection_name: str, embeddings: EmbeddingProvider) -> None:
        try:
            import chromadb
        except ImportError as exc:  # pragma: no cover - depends on environment setup
            raise RuntimeError(
                "chromadb is not installed. Run: pip install -r requirements.txt"
            ) from exc

        path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(path))
        self.collection_name = collection_name
        self.embeddings = embeddings
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def reset(self) -> None:
        try:
            self.client.delete_collection(self.collection_name)
        except Exception:
            pass
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(self, chunks: list[DocumentChunk], batch_size: int = 64) -> None:
        if not chunks:
            return
        for start in range(0, len(chunks), batch_size):
            batch = chunks[start : start + batch_size]
            texts = [chunk.text for chunk in batch]
            vectors = self.embeddings.embed_documents(texts)
            self.collection.upsert(
                ids=[chunk.id for chunk in batch],
                documents=texts,
                embeddings=vectors,
                metadatas=[chunk.metadata for chunk in batch],
            )

    def query(self, query_text: str, top_k: int) -> list[RetrievedChunk]:
        query_vector = self.embeddings.embed_query(query_text)
        result = self.collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        return self._to_retrieved_chunks(result)

    def count(self) -> int:
        return int(self.collection.count())

    @staticmethod
    def _to_retrieved_chunks(result: dict[str, Any]) -> list[RetrievedChunk]:
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        retrieved: list[RetrievedChunk] = []
        for chunk_id, text, metadata, distance in zip(ids, documents, metadatas, distances, strict=False):
            page_value = metadata.get("page") or 0
            location = SourceLocation(
                source=str(metadata.get("source", "unknown")),
                section=str(metadata.get("section") or "") or None,
                page=int(page_value) if page_value else None,
            )
            score = max(0.0, min(1.0, 1.0 - float(distance)))
            chunk = DocumentChunk(
                id=str(chunk_id),
                text=str(text),
                location=location,
                metadata=dict(metadata),
            )
            retrieved.append(RetrievedChunk(chunk=chunk, score=round(score, 3)))
        return retrieved
