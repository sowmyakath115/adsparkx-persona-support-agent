from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from support_agent.config import load_settings
from support_agent.workflow import KnowledgeBaseIngestor, SupportAgent


console = Console()


def _render_response(response: object) -> None:
    # The object is typed inside workflow; keeping this helper isolated improves CLI readability.
    table = Table(title="Support Agent Output", show_lines=True)
    table.add_column("Field", style="bold")
    table.add_column("Value")

    persona = response.persona
    table.add_row("User Message", response.user_message)
    table.add_row(
        "Detected Persona",
        f"{persona.persona.value} (confidence: {persona.confidence})\nReasons: "
        + "; ".join(persona.reasons),
    )

    sources = "\n".join(
        f"- {item.chunk.location.label()} | score={item.score}" for item in response.retrieved_chunks
    ) or "No sources retrieved"
    table.add_row("Retrieved Sources", sources)
    table.add_row("Generated Response", response.answer)

    escalation_text = "YES" if response.escalation.should_escalate else "NO"
    if response.escalation.reasons:
        escalation_text += "\n" + "\n".join(f"- {reason}" for reason in response.escalation.reasons)
    table.add_row("Escalation Status", escalation_text)
    console.print(table)

    if response.handoff_summary:
        console.print(
            Panel(
                json.dumps(response.handoff_summary.to_dict(), indent=2),
                title="Human Handoff Summary",
                border_style="yellow",
            )
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the persona-adaptive support chatbot.")
    parser.add_argument("--project-root", default=".", help="Project root path")
    parser.add_argument(
        "--auto-ingest",
        action="store_true",
        help="Ingest the knowledge base before starting chat",
    )
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    settings = load_settings(project_root)

    if args.auto_ingest:
        chunks = KnowledgeBaseIngestor(settings).ingest(reset=True)
        console.print(f"[green]Indexed {chunks} chunks before chat.[/green]")

    agent = SupportAgent(settings)
    console.print(
        Panel.fit(
            "Persona-Adaptive Customer Support Agent\n"
            "Type your support issue. Commands: /reset, /exit",
            title="Adsparkx AI Assignment Demo",
            border_style="cyan",
        )
    )

    while True:
        try:
            message = console.input("\n[bold cyan]Customer:[/bold cyan] ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\nGoodbye.")
            break
        if not message:
            continue
        if message.lower() in {"/exit", "exit", "quit"}:
            console.print("Goodbye.")
            break
        if message.lower() == "/reset":
            agent.reset()
            console.print("[green]Conversation memory reset.[/green]")
            continue

        response = agent.handle_message(message)
        _render_response(response)


if __name__ == "__main__":
    main()
