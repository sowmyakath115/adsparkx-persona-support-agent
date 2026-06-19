# 3-8 Minute Screen Recording Checklist

1. Show the repository structure: `src/support_agent`, `data/knowledge_base`, `config`, `README.md`.
2. Show at least one PDF in `data/knowledge_base`.
3. Run: `python -m support_agent.ingest`.
4. Run: `python -m support_agent.cli`.
5. Ask the Technical Expert query from `scripts/demo_queries.txt`.
6. Ask the Frustrated User query from `scripts/demo_queries.txt`.
7. Ask the Business Executive query from `scripts/demo_queries.txt`.
8. Ask the Billing escalation query and show the JSON handoff summary.
9. Ask the low-confidence query and show escalation.
10. Explain one design decision: deterministic persona detector plus configurable escalation rules.
