"""Annotate renderer - display annotate results."""

from rich.console import RenderableType
from rich.table import Table

from pgai_example.management.data_models import AnnotateResultsData
from pgai_example.management.renderers.base import CLIComponent


class AnnotateRenderer(CLIComponent[AnnotateResultsData, AnnotateResultsData]):
    """Renderer for annotate command display."""

    component_name = "Annotate Renderer"
    component_key = "annotate"

    def render(self, data: AnnotateResultsData) -> RenderableType:
        """Create Rich table from annotate data."""
        results = data.get("results", [])
        query = data.get("query", "")
        model_name = data.get("model_name", "")
        limit = data.get("limit", 10)

        table = Table(
            title=f"Annotate Results: '{query}' ({model_name})",
            show_header=True,
            header_style="bold cyan",
            border_style="dim",
        )
        table.add_column("#", style="dim", width=4)
        table.add_column("Title", style="white")
        table.add_column("Score", justify="right", style="yellow")

        for idx, result in enumerate(results, 1):
            table.add_row(
                str(idx),
                result.get("title", ""),
                f"{result.get('score', 0.0):.3f}",
            )

        return table
