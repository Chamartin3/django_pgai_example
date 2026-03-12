"""Rank renderer - display semantic_rank results."""

from rich.console import RenderableType
from rich.table import Table

from pgai_example.management.data_models import RankResultsData
from pgai_example.management.renderers.base import CLIComponent


class RankRenderer(CLIComponent[RankResultsData, RankResultsData]):
    """Renderer for rank command display."""

    component_name = "Rank Renderer"
    component_key = "rank"

    def render(self, data: RankResultsData) -> RenderableType:
        """Create Rich table from rank data."""
        results = data.get("results", [])
        query = data.get("query", "")
        model_name = data.get("model_name", "")

        table = Table(
            title=f"Semantic Rank: '{query}' ({model_name})",
            show_header=True,
            header_style="bold cyan",
            border_style="dim",
        )
        table.add_column("Rank", style="dim", width=6)
        table.add_column("Title", style="white")

        for result in results:
            table.add_row(
                str(result.get("rank", "")),
                result.get("title", ""),
            )

        return table
