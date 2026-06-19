from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Persona(str, Enum):
    TECHNICAL_EXPERT = "Technical Expert"
    FRUSTRATED_USER = "Frustrated User"
    BUSINESS_EXECUTIVE = "Business Executive"


@dataclass(frozen=True)
class SourceLocation:
    source: str
    section: str | None = None
    page: int | None = None

    def label(self) -> str:
        parts = [self.source]
        if self.page is not None:
            parts.append(f"page {self.page}")
        if self.section:
            parts.append(self.section)
        return " | ".join(parts)


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    text: str
    location: SourceLocation
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievedChunk:
    chunk: DocumentChunk
    score: float


@dataclass(frozen=True)
class PersonaDecision:
    persona: Persona
    confidence: float
    reasons: list[str]
    raw_scores: dict[str, float]


@dataclass
class MessageTurn:
    role: str
    content: str


@dataclass(frozen=True)
class EscalationDecision:
    should_escalate: bool
    reasons: list[str]


@dataclass(frozen=True)
class HandoffSummary:
    persona: str
    issue: str
    conversation_history: list[dict[str, str]]
    documents_used: list[str]
    attempted_steps: list[str]
    recommendation: str
    escalation_reasons: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "persona": self.persona,
            "issue": self.issue,
            "conversation_history": self.conversation_history,
            "documents_used": self.documents_used,
            "attempted_steps": self.attempted_steps,
            "recommendation": self.recommendation,
            "escalation_reasons": self.escalation_reasons,
        }


@dataclass(frozen=True)
class AgentResponse:
    user_message: str
    persona: PersonaDecision
    retrieved_chunks: list[RetrievedChunk]
    answer: str
    escalation: EscalationDecision
    handoff_summary: HandoffSummary | None = None
