"""Compare-timing renderer - latency benchmark across vectorizer variants."""

from rich.console import RenderableType
from rich.table import Table

from pgai_example.management.data_models import CompareTimingData
from pgai_example.management.renderers.base import CLIComponent


class CompareTimingRenderer(CLIComponent[CompareTimingData, CompareTimingData]):
    """Renderer for latency benchmark."""

    component_name = "Compare Timing Renderer"
    component_key = "compare_timing"

    def render(self, data: CompareTimingData) -> RenderableType:
        query = data.get("query", "")
        runs = data.get("runs", 0)
        rows = data.get("rows", [])

        table = Table(
            title=f"Latency benchmark ({runs} warm runs): '{query}'",
            show_header=True,
            header_style="bold cyan",
            border_style="dim",
        )
        table.add_column("Variant", style="cyan")
        table.add_column("Field", style="dim")
        table.add_column("mean", justify="right", style="yellow")
        table.add_column("p50", justify="right", style="white")
        table.add_column("p95", justify="right", style="white")
        table.add_column("min", justify="right", style="dim")
        table.add_column("max", justify="right", style="dim")

        for row in rows:
            table.add_row(
                row["variant_key"],
                row["field"],
                f"{row['mean_ms']:.1f}ms",
                f"{row['p50_ms']:.1f}ms",
                f"{row['p95_ms']:.1f}ms",
                f"{row['min_ms']:.1f}ms",
                f"{row['max_ms']:.1f}ms",
            )

        return table
