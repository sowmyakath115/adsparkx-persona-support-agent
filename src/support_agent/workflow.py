from __future__ import annotations

from pathlib import Path

from support_agent.chunking import TextChunker
from support_agent.config import Settings, load_settings
from support_agent.document_loader import DocumentLoader
from support_agent.embeddings import build_embedding_provider
from support_agent.escalation import EscalationEngine
from support_agent.handoff import HandoffBuilder
from support_agent.persona import PersonaDetector
from support_agent.response_generator import ResponseGenerator
from support_agent.retriever import Retriever
from support_agent.schemas import AgentResponse, MessageTurn
from support_agent.vector_store import ChromaVectorStore


class KnowledgeBaseIngestor:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.loader = DocumentLoader()
        self.chunker = TextChunker(chunk_size=900, chunk_overlap=120)
        self.embeddings = build_embedding_provider(settings)
        self.vector_store = ChromaVectorStore(
            path=settings.resolved_vector_db_path,
            collection_name=settings.collection_name,
            embeddings=self.embeddings,
        )

    def ingest(self, reset: bool = True) -> int:
        documents = self.loader.load_directory(self.settings.resolved_kb_dir)
        chunks = self.chunker.chunk_documents(documents)
        if reset:
            self.vector_store.reset()
        self.vector_store.upsert_chunks(chunks)
        return len(chunks)


class SupportAgent:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        embeddings = build_embedding_provider(settings)
        vector_store = ChromaVectorStore(
            path=settings.resolved_vector_db_path,
            collection_name=settings.collection_name,
            embeddings=embeddings,
        )
        self.detector = PersonaDetector()
        self.retriever = Retriever(vector_store=vector_store, top_k=settings.top_k)
        self.generator = ResponseGenerator(settings)
        self.escalation = EscalationEngine(settings.escalation)
        self.handoff = HandoffBuilder()
        self.history: list[MessageTurn] = []

    @classmethod
    def from_project_root(cls, project_root: Path | None = None) -> "SupportAgent":
        return cls(load_settings(project_root))

    def reset(self) -> None:
        self.history.clear()

    def handle_message(self, user_message: str) -> AgentResponse:
        persona = self.detector.detect(user_message)
        retrieved = self.retriever.retrieve(user_message)
        escalation = self.escalation.evaluate(user_message, retrieved, self.history)
        answer = self.generator.generate(
            user_message=user_message,
            persona=persona,
            retrieved=retrieved,
            history=self.history,
        )
        handoff = None
        if escalation.should_escalate:
            handoff = self.handoff.build(
                persona=persona,
                user_message=user_message,
                retrieved=retrieved,
                history=self.history,
                escalation_reasons=escalation.reasons,
            )
        self.history.append(MessageTurn(role="user", content=user_message))
        self.history.append(MessageTurn(role="assistant", content=answer))
        return AgentResponse(
            user_message=user_message,
            persona=persona,
            retrieved_chunks=retrieved,
            answer=answer,
            escalation=escalation,
            handoff_summary=handoff,
        )
