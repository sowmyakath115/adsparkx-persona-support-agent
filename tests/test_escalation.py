from support_agent.config import EscalationConfig
from support_agent.escalation import EscalationEngine
from support_agent.schemas import MessageTurn


def test_escalates_when_no_retrieval() -> None:
    engine = EscalationEngine(EscalationConfig())
    decision = engine.evaluate("My issue is unknown", [], [])
    assert decision.should_escalate


def test_escalates_for_sensitive_billing_issue() -> None:
    engine = EscalationEngine(EscalationConfig())
    decision = engine.evaluate("I need a refund for an unauthorized charge", [], [])
    assert decision.should_escalate
    assert any("Sensitive" in reason for reason in decision.reasons)


def test_escalates_after_repeated_dissatisfaction() -> None:
    engine = EscalationEngine(EscalationConfig(escalate_after_dissatisfied_turns=2))
    history = [MessageTurn("user", "It is still not solved"), MessageTurn("assistant", "Try this")]
    decision = engine.evaluate("Same issue, nothing works", [], history)
    assert decision.should_escalate
