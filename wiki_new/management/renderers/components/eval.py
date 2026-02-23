"""Eval renderer for evaluation results display."""
from rich.console import RenderableType
from rich.table import Table
from wiki_new.management.renderers.base import CLIComponent


class EvalRenderer(CLIComponent):
    """Renderer for evaluation results."""
    component_name = 'Eval Renderer'
    component_key = 'eval'

    def render(self, results: list) -> RenderableType:
        """Create Rich table from evaluation results list."""
        table = Table(
            title="Evaluation Results",
            show_header=True,
            header_style="bold cyan",
        )
        table.add_column("Test", style="cyan", min_width=20)
        table.add_column("Matches", style="white", min_width=50)
        table.add_column("Time (ms)", style="dim", min_width=10, justify="right")

        for result in results:
            if result.get('status') == 'error':
                table.add_row(
                    result.get('name', 'Unknown'),
                    f"[red]{result.get('error', 'Unknown error')}[/red]",
                    str(result.get('elapsed_ms', 0)),
                    end_section=True,
                )
                continue

            samples = result.get('samples', [])
            samples_str = '\n'.join(f'• {s}' for s in samples) if samples else '[dim]No results[/dim]'
            table.add_row(
                result.get('name', 'Unknown'),
                samples_str,
                str(result.get('elapsed_ms', 0)),
                end_section=True,
            )

        return table
