from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from support_agent.config import load_settings
from support_agent.workflow import KnowledgeBaseIngestor


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest knowledge base documents into ChromaDB.")
    parser.add_argument("--project-root", default=".", help="Project root path")
    parser.add_argument("--no-reset", action="store_true", help="Append to existing collection")
    args = parser.parse_args()

    console = Console()
    project_root = Path(args.project_root).resolve()
    settings = load_settings(project_root)
    ingestor = KnowledgeBaseIngestor(settings)
    chunk_count = ingestor.ingest(reset=not args.no_reset)

    console.print(
        Panel.fit(
            f"Knowledge base ingestion complete.\nChunks indexed: [bold]{chunk_count}[/bold]\n"
            f"Vector DB: {settings.resolved_vector_db_path}\nCollection: {settings.collection_name}",
            title="Ingestion Complete",
            border_style="green",
        )
    )


if __name__ == "__main__":
    main()
