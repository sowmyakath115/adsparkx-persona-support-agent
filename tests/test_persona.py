from support_agent.persona import PersonaDetector
from support_agent.schemas import Persona


def test_detects_technical_expert() -> None:
    decision = PersonaDetector().detect(
        "Can you explain why the API returns 401 and what logs or OAuth scopes I should check?"
    )
    assert decision.persona == Persona.TECHNICAL_EXPERT


def test_detects_frustrated_user() -> None:
    decision = PersonaDetector().detect("I've tried everything and it is still not working!")
    assert decision.persona == Persona.FRUSTRATED_USER


def test_detects_business_executive() -> None:
    decision = PersonaDetector().detect("What is the business impact, ETA, and operational risk?")
    assert decision.persona == Persona.BUSINESS_EXECUTIVE
