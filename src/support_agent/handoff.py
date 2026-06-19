from __future__ import annotations

import re

from support_agent.schemas import HandoffSummary, MessageTurn, PersonaDecision, RetrievedChunk


class HandoffBuilder:
    def build(
        self,
        persona: PersonaDecision,
        user_message: str,
        retrieved: list[RetrievedChunk],
        history: list[MessageTurn],
        escalation_reasons: list[str],
    ) -> HandoffSummary:
        documents = []
        for item in retrieved:
            source = item.chunk.location.source
            if source not in documents:
                documents.append(source)

        attempted_steps = self._extract_attempted_steps(history + [MessageTurn("user", user_message)])
        recommendation = self._recommendation(escalation_reasons, retrieved)
        issue = self._issue_summary(user_message)

        return HandoffSummary(
            persona=persona.persona.value,
            issue=issue,
            conversation_history=[{"role": turn.role, "content": turn.content} for turn in history[-8:]]
            + [{"role": "user", "content": user_message}],
            documents_used=documents,
            attempted_steps=attempted_steps,
            recommendation=recommendation,
            escalation_reasons=escalation_reasons,
        )

    @staticmethod
    def _issue_summary(user_message: str) -> str:
        compact = re.sub(r"\s+", " ", user_message).strip()
        return compact[:180] + ("..." if len(compact) > 180 else "")

    @staticmethod
    def _extract_attempted_steps(history: list[MessageTurn]) -> list[str]:
        joined = " ".join(turn.content.lower() for turn in history)
        candidates = {
            "Password reset": ["reset password", "password reset"],
            "Browser cache clear": ["cache", "cookies"],
            "Retry after waiting": ["retry", "tried again"],
            "Checked logs": ["logs", "trace", "request id"],
            "Verified configuration": ["config", "configuration", "settings"],
            "Checked billing/invoice details": ["billing", "invoice", "payment"],
            "Reviewed account/security status": ["account", "security", "lock"],
        }
        steps = [label for label, keywords in candidates.items() if any(keyword in joined for keyword in keywords)]
        return steps or ["Initial knowledge base lookup completed"]

    @staticmethod
    def _recommendation(escalation_reasons: list[str], retrieved: list[RetrievedChunk]) -> str:
        reason_text = " ".join(escalation_reasons).lower()
        if "sensitive" in reason_text or "billing" in reason_text:
            return "Route to authorized support representative for account, billing, legal, or compliance review."
        if "low" in reason_text or not retrieved:
            return "Ask human support to investigate because available documentation did not provide a reliable answer."
        return "Continue with human-assisted troubleshooting and preserve retrieved sources for context."
