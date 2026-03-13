"""Stats renderer - display vectorization progress table."""

from rich.console import RenderableType
from rich.table import Table

from pgai_example.management.data_models import StatsData
from pgai_example.management.renderers.base import CLIComponent


class StatsRenderer(CLIComponent[StatsData, StatsData]):
    """Renderer for stats command display."""

    component_name = "Stats Renderer"
    component_key = "stats"

    def render(self, data: StatsData) -> RenderableType:
        """Create Rich table from stats data."""
        rows = data.get("rows", [])
        variant = data.get("variant", "all")

        table = Table(
            title=f"Vectorization Progress (variant: {variant})",
            show_header=True,
            header_style="bold cyan",
            border_style="dim",
        )
        table.add_column("Model", style="cyan")
        table.add_column("Field", style="magenta")
        table.add_column("Total", justify="right")
        table.add_column("Embedded", justify="right")
        table.add_column("%", justify="right", style="yellow")

        for row in rows:
            percent = row.get("percent", 0.0)
            table.add_row(
                row.get("model_name", ""),
                row.get("field_name", ""),
                str(row.get("total_rows", 0)),
                str(row.get("embedded_rows", 0)),
                f"{percent:.1f}%",
            )

        return table
