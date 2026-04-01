"""Compare results - same query across all vectorizer variants."""

from typer import Argument, Option

from pgai_example.management.context import ctx
from pgai_example.management.commands._sample.usage.compare._runner import (
    collect_results,
)


def handle_results(query: str, limit: int) -> None:
    try:
        data = collect_results(query=query, limit=limit)
        ctx.render.compare_models.print(data)
    except Exception as e:
        ctx.render.message.error(f"Compare results failed: {e}")


class CompareResultsCommand:
    """Typer adapter for `compare models results`."""

    @staticmethod
    def results(
        query: str = Argument(..., help="Search query"),
        limit: int = Option(5, "--limit", "-l", help="Top-N per variant"),
    ):
        """Same query, all variants, side-by-side top-N."""
        handle_results(query=query, limit=limit)


resultsCommand = CompareResultsCommand()
