from __future__ import annotations

from support_agent.config import EscalationConfig
from support_agent.schemas import EscalationDecision, MessageTurn, RetrievedChunk


class EscalationEngine:
    DISSATISFACTION_MARKERS = (
        "still not",
        "not solved",
        "doesn't work",
        "does not work",
        "same issue",
        "angry",
        "frustrated",
        "useless",
        "tried everything",
        "nothing works",
    )

    def __init__(self, config: EscalationConfig) -> None:
        self.config = config

    def evaluate(
        self,
        user_message: str,
        retrieved: list[RetrievedChunk],
        history: list[MessageTurn],
    ) -> EscalationDecision:
        reasons: list[str] = []
        normalized = user_message.lower()

        if not retrieved:
            reasons.append("No relevant knowledge base documents were retrieved.")
        else:
            top_score = max(item.score for item in retrieved)
            if top_score < self.config.min_retrieval_score:
                reasons.append(
                    f"Retrieval confidence is low: top score {top_score:.2f} is below "
                    f"threshold {self.config.min_retrieval_score:.2f}."
                )

        matched_sensitive = [keyword for keyword in self.config.sensitive_keywords if keyword in normalized]
        if matched_sensitive:
            reasons.append(
                "Sensitive topic detected: " + ", ".join(sorted(set(matched_sensitive))[:5]) + "."
            )

        dissatisfied_turns = self._count_recent_dissatisfaction(history + [MessageTurn("user", user_message)])
        if dissatisfied_turns >= self.config.escalate_after_dissatisfied_turns:
            reasons.append(
                f"User appears dissatisfied across {dissatisfied_turns} recent turn(s), meeting escalation policy."
            )

        return EscalationDecision(should_escalate=bool(reasons), reasons=reasons)

    def _count_recent_dissatisfaction(self, history: list[MessageTurn]) -> int:
        user_turns = [turn.content.lower() for turn in history if turn.role == "user"][-4:]
        count = 0
        for message in user_turns:
            if any(marker in message for marker in self.DISSATISFACTION_MARKERS):
                count += 1
        return count
