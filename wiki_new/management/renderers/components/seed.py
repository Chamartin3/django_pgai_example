"""Seed renderer - displays seed operation results."""
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from wiki_new.management.data_models import SeedResultsData
from wiki_new.management.renderers.base import CLIComponent


class SeedRenderer(CLIComponent[SeedResultsData, SeedResultsData]):
    """Renderer for seed operation results."""

    component_name = 'Seed Renderer'
    component_key = 'seed'

    def render(self, data: SeedResultsData) -> RenderableType:
        """Render seed results as Rich panels and tables.

        Args:
            data: Seed results data

        Returns:
            RenderableType: Rich renderable for console output
        """
        output = []

        # Header panel
        header_text = Text()
        header_text.append("Loading Wikipedia Data\n", style="bold cyan")
        header_text.append(f"Batches: {data['batches']}, ", style="dim")
        header_text.append(f"Batch size: {data['batch_size']}\n", style="dim")
        header_text.append(
            f"Total per model: {data['total_per_model']} articles",
            style="dim"
        )

        output.append(Panel(header_text, border_style="cyan"))
        output.append("")

        # Tables results table
        table = Table(
            title="Table Loading Results",
            show_header=True,
            header_style="bold",
            border_style="dim",
        )

        table.add_column("Table", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Articles Loaded", justify="right", style="green")
        table.add_column("Error", style="red")

        for table_result in data['tables']:
            status_icon = "✓" if table_result['success'] else "✗"
            status_style = "green" if table_result['success'] else "red"
            status = Text(status_icon, style=status_style)

            articles = str(table_result['total_loaded']) if table_result['success'] else "-"
            error = table_result['error'] or ""

            table.add_row(
                table_result['table_name'],
                status,
                articles,
                error[:50] + "..." if len(error) > 50 else error,
            )

        output.append(table)
        output.append("")

        # Summary panel
        summary_text = Text()
        summary_text.append("Summary\n", style="bold cyan")
        summary_text.append(
            f"Tables processed: {len(data['tables'])}\n",
            style="dim"
        )
        summary_text.append(
            f"Successful: {data['success_count']}\n",
            style="green" if data['success_count'] > 0 else "dim"
        )
        summary_text.append(
            f"Failed: {data['failed_count']}",
            style="red" if data['failed_count'] > 0 else "dim"
        )

        output.append(Panel(summary_text, border_style="cyan"))

        # Combine all renderables
        from rich.console import Group
        return Group(*output)
