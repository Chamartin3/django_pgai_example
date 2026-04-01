"""Compare-models renderer - side-by-side top-N across vectorizer variants."""

from rich.console import RenderableType
from rich.table import Table

from pgai_example.management.data_models import CompareModelsData
from pgai_example.management.renderers.base import CLIComponent


class CompareModelsRenderer(CLIComponent[CompareModelsData, CompareModelsData]):
    """Renderer for cross-vectorizer comparison."""

    component_name = "Compare Models Renderer"
    component_key = "compare_models"

    def render(self, data: CompareModelsData) -> RenderableType:
        query = data.get("query", "")
        columns = data.get("columns", [])
        limit = data.get("limit", 0)

        table = Table(
            title=f"Compare vectorizers (top {limit}): '{query}'",
            show_header=True,
            header_style="bold cyan",
            border_style="dim",
        )
        table.add_column("#", style="dim", width=3)
        for col in columns:
            table.add_column(
                f"{col['variant_key']}\n[dim]{col['field']}[/dim]",
                style="white",
                overflow="fold",
            )

        max_rows = max((len(c["hits"]) for c in columns), default=0)
        for i in range(max_rows):
            row = [str(i + 1)]
            for col in columns:
                hits = col["hits"]
                if i < len(hits):
                    h = hits[i]
                    row.append(f"{h['title']}\n[yellow]{h['score']:.3f}[/yellow]")
                else:
                    row.append("[dim]—[/dim]")
            table.add_row(*row)

        return table
