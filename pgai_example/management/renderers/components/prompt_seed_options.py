"""Prompt renderer for seed command interactive options.

This component handles the interactive prompt when a table already has data,
prompting the user to choose between replace, append, or skip.
"""
from rich.console import RenderableType
from rich.text import Text
from pgai_example.management.data_models import SeedAction
from pgai_example.management.renderers.base import CLIComponent


class PromptSeedOptionsRenderer(CLIComponent[dict, dict]):
    """Interactive prompt for seed data replacement options."""

    component_name = 'Prompt Seed Options Renderer'
    component_key = 'prompt_seed_options'

    # Expose SeedAction enum for handlers to use
    option = SeedAction

    def render(self, data: dict) -> RenderableType:
        """This renderer doesn't use the standard render flow."""
        return Text("")

    def prompt_action(
        self,
        variant_key: str,
        existing_count: int,
        new_total: int,
    ) -> SeedAction:
        """Prompt user for action when table has existing data.

        Args:
            variant_key: The variant being loaded (e.g., 'minilm')
            existing_count: Number of existing registries
            new_total: Number of new registries to load

        Returns:
            SeedAction: User's choice enum value
        """
        # Display existing data message
        self.console.print(
            f"\n[yellow]Sample Data \"[bold cyan]{variant_key}[/bold cyan][yellow]\" "
            f"already has [bold green]{existing_count}[/bold green][yellow] registries.[/yellow]"
        )

        try:
            # Build prompt with colored number
            prompt_text = "[cyan]Replace existing data with new [bold green]"
            prompt_text += str(new_total)
            prompt_text += "[/bold green][cyan] registries? (replace/r, append/a, skip/s) [skip]: [/cyan]"
            response = self.console.input(prompt_text).lower().strip() or "skip"
        except KeyboardInterrupt:
            self.console.print("\n[dim]Keyboard interrupt - skipping this table[/dim]\n")
            return SeedAction.SKIP

        # Expand shortcuts
        if response in ("replace", "r"):
            return SeedAction.REPLACE
        elif response in ("append", "a"):
            return SeedAction.APPEND
        else:
            return SeedAction.SKIP

    def display_cleared(self, count: int) -> None:
        """Display success message after clearing table.

        Args:
            count: Number of registries cleared
        """
        self.console.print(f"[green]✓ Cleared {count} registries[/green]\n")

    def display_appending(self) -> None:
        """Display message that data will be appended."""
        self.console.print("[dim]Appending new data to existing registries[/dim]\n")

    def display_skipping(self) -> None:
        """Display message that table will be skipped."""
        self.console.print("[dim]Skipping this table[/dim]\n")
