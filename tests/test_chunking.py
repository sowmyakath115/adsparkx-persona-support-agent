from support_agent.chunking import TextChunker
from support_agent.document_loader import LoadedDocument
from support_agent.schemas import SourceLocation


def test_chunk_metadata_is_preserved() -> None:
    doc = LoadedDocument(
        text="A" * 1200,
        location=SourceLocation(source="sample.md", section="Troubleshooting"),
    )
    chunks = TextChunker(chunk_size=500, chunk_overlap=50).chunk_documents([doc])
    assert len(chunks) >= 2
    assert all(chunk.metadata["source"] == "sample.md" for chunk in chunks)
    assert all(chunk.metadata["section"] == "Troubleshooting" for chunk in chunks)
