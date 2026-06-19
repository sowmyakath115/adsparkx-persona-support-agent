from __future__ import annotations

import re
from collections import Counter

from support_agent.schemas import Persona, PersonaDecision


class PersonaDetector:
    """Lightweight, explainable persona classifier.

    The assignment values understanding and transparency. A deterministic classifier is useful here
    because the UI can show why a persona was selected. It can be swapped with an LLM classifier
    later without changing the workflow contract.
    """

    TECHNICAL_TERMS = {
        "api",
        "auth",
        "authentication",
        "oauth",
        "token",
        "jwt",
        "logs",
        "stacktrace",
        "trace",
        "config",
        "configuration",
        "webhook",
        "payload",
        "endpoint",
        "status code",
        "500",
        "401",
        "403",
        "sso",
        "saml",
        "scim",
        "dns",
        "curl",
        "latency",
    }
    FRUSTRATED_TERMS = {
        "angry",
        "annoyed",
        "frustrated",
        "nothing works",
        "tried everything",
        "again",
        "still not",
        "urgent",
        "asap",
        "immediately",
        "terrible",
        "waste",
        "fed up",
        "not working",
        "broken",
        "can't login",
        "cannot login",
    }
    EXECUTIVE_TERMS = {
        "business impact",
        "operations",
        "sla",
        "eta",
        "timeline",
        "resolved",
        "resolution",
        "customers affected",
        "risk",
        "revenue",
        "downtime",
        "executive",
        "summary",
        "status update",
        "impact",
        "priority",
    }

    def detect(self, message: str) -> PersonaDecision:
        normalized = message.lower().strip()
        tokens = Counter(re.findall(r"[a-zA-Z0-9_/-]+", normalized))

        scores = {
            Persona.TECHNICAL_EXPERT.value: 0.0,
            Persona.FRUSTRATED_USER.value: 0.0,
            Persona.BUSINESS_EXECUTIVE.value: 0.0,
        }
        reasons: list[str] = []

        self._score_terms(
            normalized,
            tokens,
            self.TECHNICAL_TERMS,
            Persona.TECHNICAL_EXPERT,
            scores,
            reasons,
            "technical support language",
        )
        self._score_terms(
            normalized,
            tokens,
            self.FRUSTRATED_TERMS,
            Persona.FRUSTRATED_USER,
            scores,
            reasons,
            "urgency or dissatisfaction cues",
        )
        self._score_terms(
            normalized,
            tokens,
            self.EXECUTIVE_TERMS,
            Persona.BUSINESS_EXECUTIVE,
            scores,
            reasons,
            "business impact language",
        )

        if "?" in message and len(message.split()) > 18:
            scores[Persona.TECHNICAL_EXPERT.value] += 0.4
            reasons.append("long diagnostic question")
        if message.count("!") >= 1 or message.isupper():
            scores[Persona.FRUSTRATED_USER.value] += 0.5
            reasons.append("emphatic punctuation or capitalization")
        if len(message.split()) <= 18 and any(word in normalized for word in ["eta", "impact", "summary"]):
            scores[Persona.BUSINESS_EXECUTIVE.value] += 0.5
            reasons.append("concise outcome-oriented request")

        # Sensible default for neutral support questions: frustrated user gets simple language.
        if max(scores.values()) == 0:
            scores[Persona.FRUSTRATED_USER.value] = 0.25
            reasons.append("neutral request defaulted to simple customer support tone")

        persona_name, top_score = max(scores.items(), key=lambda item: item[1])
        score_sum = sum(scores.values()) or 1.0
        confidence = round(top_score / score_sum, 2)
        return PersonaDecision(
            persona=Persona(persona_name),
            confidence=confidence,
            reasons=reasons[:5],
            raw_scores={key: round(value, 2) for key, value in scores.items()},
        )

    @staticmethod
    def _score_terms(
        normalized: str,
        tokens: Counter[str],
        terms: set[str],
        persona: Persona,
        scores: dict[str, float],
        reasons: list[str],
        reason_label: str,
    ) -> None:
        matched: list[str] = []
        for term in terms:
            if " " in term:
                if term in normalized:
                    matched.append(term)
                    scores[persona.value] += 1.2
            elif tokens[term] > 0:
                matched.append(term)
                scores[persona.value] += 1.0
        if matched:
            reasons.append(f"Matched {reason_label}: {', '.join(sorted(matched)[:4])}")
