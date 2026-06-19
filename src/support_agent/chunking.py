from __future__ import annotations

import hashlib
import re

from support_agent.document_loader import LoadedDocument
from support_agent.schemas import DocumentChunk


class TextChunker:
    def __init__(self, chunk_size: int = 900, chunk_overlap: int = 120) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_documents(self, documents: list[LoadedDocument]) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []
        for document in documents:
            for text in self._chunk_text(document.text):
                chunk_id = self._make_id(document.location.label(), text)
                chunks.append(
                    DocumentChunk(
                        id=chunk_id,
                        text=text,
                        location=document.location,
                        metadata={
                            "source": document.location.source,
                            "section": document.location.section or "",
                            "page": document.location.page or 0,
                        },
                    )
                )
        return chunks

    def _chunk_text(self, text: str) -> list[str]:
        normalized = re.sub(r"\n{3,}", "\n\n", text).strip()
        if len(normalized) <= self.chunk_size:
            return [normalized]

        paragraphs = re.split(r"\n\s*\n", normalized)
        chunks: list[str] = []
        current = ""

        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            if len(current) + len(paragraph) + 2 <= self.chunk_size:
                current = f"{current}\n\n{paragraph}".strip()
                continue

            if current:
                chunks.append(current)
                current = self._tail_overlap(current)

            if len(paragraph) > self.chunk_size:
                chunks.extend(self._split_long_paragraph(paragraph))
                current = ""
            else:
                current = f"{current}\n\n{paragraph}".strip()

        if current:
            chunks.append(current)
        return [chunk for chunk in chunks if chunk.strip()]

    def _split_long_paragraph(self, paragraph: str) -> list[str]:
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        if len(sentences) == 1 and len(sentences[0]) > self.chunk_size:
            chunks: list[str] = []
            step = max(1, self.chunk_size - self.chunk_overlap)
            for start in range(0, len(paragraph), step):
                window = paragraph[start : start + self.chunk_size].strip()
                if window:
                    chunks.append(window)
                if start + self.chunk_size >= len(paragraph):
                    break
            return chunks

        chunks = []
        current = ""
        for sentence in sentences:
            if len(current) + len(sentence) + 1 <= self.chunk_size:
                current = f"{current} {sentence}".strip()
            else:
                if current:
                    chunks.append(current)
                current = sentence[-self.chunk_size :]
        if current:
            chunks.append(current)
        return chunks

    def _tail_overlap(self, text: str) -> str:
        if self.chunk_overlap <= 0:
            return ""
        return text[-self.chunk_overlap :]

    @staticmethod
    def _make_id(location_label: str, text: str) -> str:
        digest = hashlib.sha256(f"{location_label}\n{text}".encode("utf-8")).hexdigest()[:16]
        safe_source = re.sub(r"[^a-zA-Z0-9]+", "-", location_label.lower()).strip("-")[:60]
        return f"{safe_source}-{digest}"
