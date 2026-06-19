from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from support_agent.config import load_settings
from support_agent.workflow import KnowledgeBaseIngestor, SupportAgent


st.set_page_config(page_title="Persona-Adaptive Support Agent", page_icon="🤖", layout="wide")
st.title("Persona-Adaptive Customer Support Agent")
st.caption("RAG + persona-aware responses + configurable human escalation")

project_root = Path.cwd()
settings = load_settings(project_root)

with st.sidebar:
    st.header("Controls")
    if st.button("Re-ingest knowledge base"):
        count = KnowledgeBaseIngestor(settings).ingest(reset=True)
        st.success(f"Indexed {count} chunks")
    if st.button("Reset conversation"):
        st.session_state.pop("agent", None)
        st.success("Conversation reset")
    st.write("Top-k", settings.top_k)
    st.write("Min retrieval score", settings.escalation.min_retrieval_score)

if "agent" not in st.session_state:
    st.session_state.agent = SupportAgent(settings)

message = st.chat_input("Describe your support issue")
if message:
    with st.chat_message("user"):
        st.write(message)
    response = st.session_state.agent.handle_message(message)
    with st.chat_message("assistant"):
        st.subheader("Detected persona")
        st.write(f"{response.persona.persona.value} — confidence {response.persona.confidence}")
        st.caption("; ".join(response.persona.reasons))

        st.subheader("Retrieved sources")
        for item in response.retrieved_chunks:
            st.write(f"- {item.chunk.location.label()} | score={item.score}")

        st.subheader("Response")
        st.write(response.answer)

        st.subheader("Escalation")
        st.write("Escalated" if response.escalation.should_escalate else "Not escalated")
        for reason in response.escalation.reasons:
            st.warning(reason)

        if response.handoff_summary:
            st.subheader("Human handoff summary")
            st.json(response.handoff_summary.to_dict())
else:
    st.info("Run `python -m support_agent.ingest` first, then ask a support question.")
