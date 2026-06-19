from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml
from dotenv import load_dotenv


@dataclass(frozen=True)
class EscalationConfig:
    min_retrieval_score: float = 0.35
    escalate_after_dissatisfied_turns: int = 2
    sensitive_keywords: tuple[str, ...] = (
        "billing",
        "refund",
        "invoice dispute",
        "legal",
        "contract",
        "account owner",
        "data deletion",
        "security breach",
        "unauthorized charge",
        "compliance",
    )
    low_confidence_message: str = "I could not find enough reliable documentation to answer this safely."


@dataclass(frozen=True)
class Settings:
    project_root: Path = field(default_factory=lambda: Path.cwd())
    knowledge_base_dir: Path = Path("data/knowledge_base")
    vector_db_path: Path = Path("storage/chroma")
    collection_name: str = "cloudops_support_kb"
    top_k: int = 4
    llm_provider: str = "local"
    embedding_provider: str = "local"
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_api_key: str | None = None
    escalation: EscalationConfig = field(default_factory=EscalationConfig)

    @property
    def resolved_kb_dir(self) -> Path:
        return self._resolve(self.knowledge_base_dir)

    @property
    def resolved_vector_db_path(self) -> Path:
        return self._resolve(self.vector_db_path)

    def _resolve(self, path: Path) -> Path:
        return path if path.is_absolute() else self.project_root / path


def _load_escalation_config(project_root: Path) -> EscalationConfig:
    config_path = project_root / "config" / "escalation_rules.yml"
    if not config_path.exists():
        return EscalationConfig()

    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return EscalationConfig(
        min_retrieval_score=float(os.getenv("MIN_RETRIEVAL_SCORE", data.get("min_retrieval_score", 0.35))),
        escalate_after_dissatisfied_turns=int(
            os.getenv(
                "ESCALATE_AFTER_DISSATISFIED_TURNS",
                data.get("escalate_after_dissatisfied_turns", 2),
            )
        ),
        sensitive_keywords=tuple(data.get("sensitive_keywords", EscalationConfig().sensitive_keywords)),
        low_confidence_message=str(
            data.get("low_confidence_message", EscalationConfig().low_confidence_message)
        ),
    )


def load_settings(project_root: Path | None = None) -> Settings:
    root = project_root or Path.cwd()
    load_dotenv(root / ".env")
    escalation = _load_escalation_config(root)
    return Settings(
        project_root=root,
        knowledge_base_dir=Path(os.getenv("KNOWLEDGE_BASE_DIR", "data/knowledge_base")),
        vector_db_path=Path(os.getenv("VECTOR_DB_PATH", "storage/chroma")),
        collection_name=os.getenv("COLLECTION_NAME", "cloudops_support_kb"),
        top_k=int(os.getenv("TOP_K", "4")),
        llm_provider=os.getenv("AGENT_LLM_PROVIDER", "local").lower(),
        embedding_provider=os.getenv("AGENT_EMBEDDING_PROVIDER", "local").lower(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        openai_api_key=os.getenv("OPENAI_API_KEY") or None,
        escalation=escalation,
    )
