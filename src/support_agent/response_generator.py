from __future__ import annotations

import re
from collections import Counter

from openai import OpenAI

from support_agent.config import Settings
from support_agent.schemas import MessageTurn, Persona, PersonaDecision, RetrievedChunk


PERSONA_STYLE_GUIDE = {
    Persona.TECHNICAL_EXPERT: (
        "Use a detailed technical tone. Include likely root cause from the retrieved context, "
        "diagnostic checks, step-by-step troubleshooting, and relevant source references."
    ),
    Persona.FRUSTRATED_USER: (
        "Use an empathetic, calm tone. Avoid jargon. Keep steps simple, reassuring, and action-oriented."
    ),
    Persona.BUSINESS_EXECUTIVE: (
        "Use a concise business tone. Focus on impact, risk, current status, and resolution guidance. "
        "Avoid unnecessary technical detail."
    ),
}


class ResponseGenerator:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def generate(
        self,
        user_message: str,
        persona: PersonaDecision,
        retrieved: list[RetrievedChunk],
        history: list[MessageTurn],
        force_local: bool = False,
    ) -> str:
        if not retrieved:
            return self._fallback_no_context(persona)
        if self.settings.llm_provider == "openai" and self.client and not force_local:
            return self._generate_with_openai(user_message, persona, retrieved, history)
        return self._generate_local(user_message, persona, retrieved)

    def _generate_with_openai(
        self,
        user_message: str,
        persona: PersonaDecision,
        retrieved: list[RetrievedChunk],
        history: list[MessageTurn],
    ) -> str:
        context = self._format_context(retrieved)
        recent_history = "\n".join(f"{turn.role}: {turn.content}" for turn in history[-6:])
        system_prompt = f"""
You are a persona-adaptive customer support agent for CloudOps Desk.

Hard rules:
- Answer only using the retrieved knowledge base context.
- Do not invent policies, timelines, compensation, account states, or private data.
- If the context is insufficient, say that a human support representative should review it.
- Cite sources inline using [source: document | section/page].
- Follow the persona style guide exactly.

Detected persona: {persona.persona.value}
Persona style guide: {PERSONA_STYLE_GUIDE[persona.persona]}
""".strip()
        user_prompt = f"""
Conversation history:
{recent_history or "No previous turns."}

Retrieved context:
{context}

Customer message:
{user_message}

Write the support response.
""".strip()
        response = self.client.chat.completions.create(
            model=self.settings.openai_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or "I could not generate a grounded response."

    def _generate_local(
        self,
        user_message: str,
        persona: PersonaDecision,
        retrieved: list[RetrievedChunk],
    ) -> str:
        evidence = self._extract_evidence(user_message, retrieved)
        sources = self._source_list(retrieved)

        if persona.persona == Persona.TECHNICAL_EXPERT:
            steps = "\n".join(f"{idx}. {item}" for idx, item in enumerate(evidence[:5], start=1))
            return (
                "Based on the retrieved support documentation, the most likely resolution path is:\n\n"
                f"Root-cause focus: {evidence[0] if evidence else 'The documentation points to configuration or policy checks.'}\n\n"
                "Troubleshooting steps:\n"
                f"{steps}\n\n"
                "Validation: retry the affected workflow after each change and capture status code, "
                "timestamp, request ID, and tenant/user identifier for support if escalation is needed.\n\n"
                f"Sources: {sources}"
            )

        if persona.persona == Persona.FRUSTRATED_USER:
            bullets = "\n".join(f"- {self._simplify(item)}" for item in evidence[:4])
            return (
                "I understand how frustrating this is. Let us handle it step by step.\n\n"
                f"{bullets}\n\n"
                "After trying these steps, check once more. If it still does not work, I will prepare a "
                "handoff summary so a support representative can continue without making you repeat everything.\n\n"
                f"Sources: {sources}"
            )

        bullets = "\n".join(f"- {self._business_summary(item)}" for item in evidence[:3])
        return (
            "Here is the concise support summary based on the knowledge base:\n\n"
            f"{bullets}\n\n"
            "Recommended next step: continue with the documented remediation path. Escalate to support if "
            "the documented checks do not restore the workflow or if account, billing, legal, or compliance "
            "approval is involved.\n\n"
            f"Sources: {sources}"
        )

    @staticmethod
    def _format_context(retrieved: list[RetrievedChunk]) -> str:
        blocks = []
        for item in retrieved:
            blocks.append(
                f"[source: {item.chunk.location.label()} | score: {item.score}]\n{item.chunk.text}"
            )
        return "\n\n---\n\n".join(blocks)

    @staticmethod
    def _extract_evidence(user_message: str, retrieved: list[RetrievedChunk]) -> list[str]:
        query_terms = set(re.findall(r"[a-zA-Z0-9_/-]+", user_message.lower()))
        scored_sentences: list[tuple[int, str]] = []
        for item in retrieved:
            sentences = re.split(r"(?<=[.!?])\s+|\n+-\s+", item.chunk.text)
            for sentence in sentences:
                clean = re.sub(r"\s+", " ", sentence).strip(" -\n")
                if len(clean) < 24:
                    continue
                sentence_terms = Counter(re.findall(r"[a-zA-Z0-9_/-]+", clean.lower()))
                overlap = sum(1 for term in query_terms if sentence_terms[term] > 0)
                scored_sentences.append((overlap, clean))
        scored_sentences.sort(key=lambda row: row[0], reverse=True)

        evidence: list[str] = []
        seen: set[str] = set()
        for _, sentence in scored_sentences:
            normalized = sentence.lower()
            if normalized not in seen:
                evidence.append(sentence)
                seen.add(normalized)
            if len(evidence) >= 6:
                break
        return evidence or [item.chunk.text.split("\n", maxsplit=1)[0] for item in retrieved[:3]]

    @staticmethod
    def _source_list(retrieved: list[RetrievedChunk]) -> str:
        labels: list[str] = []
        for item in retrieved:
            label = item.chunk.location.label()
            if label not in labels:
                labels.append(label)
        return "; ".join(labels)

    @staticmethod
    def _simplify(sentence: str) -> str:
        simplified = sentence.replace("authenticate", "sign in").replace("credentials", "login details")
        simplified = simplified.replace("configuration", "settings")
        return simplified

    @staticmethod
    def _business_summary(sentence: str) -> str:
        sentence = re.sub(r"\b(API|JWT|SAML|SCIM|OAuth)\b", "technical workflow", sentence)
        return sentence

    @staticmethod
    def _fallback_no_context(persona: PersonaDecision) -> str:
        if persona.persona == Persona.FRUSTRATED_USER:
            return (
                "I am sorry this is taking extra effort. I could not find a reliable article for this exact "
                "issue, so I should escalate it to a human support representative."
            )
        if persona.persona == Persona.BUSINESS_EXECUTIVE:
            return (
                "I do not have enough documented information to provide a reliable business-impact answer. "
                "This should be escalated for human review."
            )
        return (
            "I could not find enough relevant documentation to provide a safe technical answer. "
            "This should be escalated with logs, request IDs, timestamps, and tenant details."
        )
