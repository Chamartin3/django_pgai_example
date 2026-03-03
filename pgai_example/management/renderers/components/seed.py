"""Seed renderer - displays seed operation results."""
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pgai_example.management.data_models import SeedResultsData
from pgai_example.management.renderers.base import CLIComponent


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
        header_text.append(f"Total registries: {data['total']}, ", style="dim")
        header_text.append(f"Batch size: {data['batch_size']}, ", style="dim")
        header_text.append(f"Batches: {data['batches']}\n", style="dim")
        header_text.append(
            f"Variant: {data['variant']}",
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

        table.add_column("Variant", style="magenta")
        table.add_column("Table", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Existing Registries", justify="right", style="dim")
        table.add_column("New Registries", justify="right", style="green")
        table.add_column("Message", style="dim")

        for table_result in data['tables']:
            if table_result.success:
                status_icon = "✓"
                status_style = "green"
            elif table_result.message:
                status_icon = "⊘"
                status_style = "yellow"
            else:
                status_icon = "✗"
                status_style = "red"

            status = Text(status_icon, style=status_style)

            existing = str(table_result.existing_count) if table_result.existing_count > 0 else "-"
            loaded = str(table_result.total_loaded) if table_result.success else "-"

            # Display message or error
            if table_result.message:
                display_text = table_result.message
                # Green for "Added", yellow for "Skipped"
                display_style = "green" if table_result.message == "Added" else "yellow"
            elif table_result.error:
                display_text = table_result.error
                display_style = "red"
            else:
                display_text = ""
                display_style = "dim"

            display_msg = Text(
                display_text[:50] + "..." if len(display_text) > 50 else display_text,
                style=display_style
            )

            table.add_row(
                table_result.variant_key,
                table_result.table_name,
                status,
                existing,
                loaded,
                display_msg,
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
            f"Skipped: {data['skipped_count']}\n",
            style="yellow" if data['skipped_count'] > 0 else "dim"
        )
        summary_text.append(
            f"Failed: {data['failed_count']}",
            style="red" if data['failed_count'] > 0 else "dim"
        )

        output.append(Panel(summary_text, border_style="cyan"))

        # Combine all renderables
        from rich.console import Group
        return Group(*output)
