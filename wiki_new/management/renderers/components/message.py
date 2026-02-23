"""Unified message renderer for errors, warnings, info, and status messages.

This component follows the CLIComponent architecture:
- print(data) -> render(parsed) -> _parse(data)
- Uses Rich console for consistent output
- Handles all message types: error, warning, success, info, no_results, incomplete
"""
from rich.console import Group, RenderableType
from rich.text import Text
from wiki_new.management.data_models import IncompleteVectorizerData, MessageType, WarningMessageType
from wiki_new.management.renderers.base import CLIComponent


class MessageRenderer(CLIComponent[dict, dict]):
    """Unified renderer for all message types (errors, warnings, info, status)."""
    component_name = 'Message Renderer'
    component_key = 'message'

    def render(self, data: dict) -> RenderableType:
        """Create Rich renderable from message data."""
        msg_type = data.get('type')
        if msg_type == MessageType.ERROR:
            message = data.get('message', 'Unknown error')
            return Text.from_markup(f'[red]✗ {message}[/red]')
        elif msg_type == MessageType.WARNING:
            message = data.get('message', 'Warning')
            return Text.from_markup(f'[yellow]⚠ {message}[/yellow]')
        elif msg_type == MessageType.SUCCESS:
            message = data.get('message', 'Success')
            return Text.from_markup(f'[green]✓ {message}[/green]')
        elif msg_type == MessageType.INFO:
            message = data.get('message', '')
            return Text.from_markup(f'[dim]{message}[/dim]')
        elif msg_type == MessageType.INCOMPLETE:
            return self._render_incomplete(data)
        elif msg_type == MessageType.NO_RESULTS:
            message = data.get('message', 'No results found')
            return Text.from_markup(f'[yellow]{message}[/yellow]')
        elif msg_type == MessageType.SUMMARY:
            message = data.get('message', '')
            return Text.from_markup(f'\n[dim]{message}[/dim]')
        return Text('')

    def _render_incomplete(self, data: dict) -> RenderableType:
        """Render warning for incomplete vectorizers."""
        model_name = data.get('model_name', 'Unknown')
        incomplete_vectorizers = data.get('incomplete_vectorizers', [])
        if not incomplete_vectorizers:
            return Text('')
        elements = []
        elements.append(Text.from_markup(f'\n[yellow]⚠ WARNING: Vectorization is not complete for {model_name}[/yellow]'))
        for v in incomplete_vectorizers:
            elements.append(Text.from_markup(
                f"  • Field '{v.get('field', 'unknown')}': {v.get('percentage', 0):.1f}% complete "
                f"({v.get('processed', 0)}/{v.get('total', 0)} rows processed)"
            ))
        elements.append(Text.from_markup('\n[dim]Results may be incomplete. Wait for vectorization to finish for best results.[/dim]'))
        elements.append(Text.from_markup('[dim]Check status: ./manage.sh cmd pgai list[/dim]\n'))
        return Group(*elements)

    def error(self, message: str) -> None:
        """Render error message."""
        self.print({
            'type': MessageType.ERROR,
            'message': message,
        })

    def warning(self, message: str) -> None:
        """Render warning message."""
        self.print({
            'type': MessageType.WARNING,
            'message': message,
        })

    def success(self, message: str) -> None:
        """Render success message."""
        self.print({
            'type': MessageType.SUCCESS,
            'message': message,
        })

    def info(self, message: str) -> None:
        """Render info message."""
        self.print({
            'type': MessageType.INFO,
            'message': message,
        })

    def render_incomplete_vectorizers(self, model_name: str, incomplete_vectorizers: list) -> None:
        """
        Render warning for incomplete vectorizers.

        Args:
            model_name: Name of the model being processed
            incomplete_vectorizers: List of dicts with vectorizer progress info
        """
        self.print({
            'type': MessageType.INCOMPLETE,
            'model_name': model_name,
            'incomplete_vectorizers': incomplete_vectorizers,
        })

    def render_no_results(self, message: str) -> None:
        """Render no results message."""
        self.print({
            'type': MessageType.NO_RESULTS,
            'message': message,
        })

    def render_summary(self, message: str) -> None:
        """Render a summary message."""
        self.print({
            'type': MessageType.SUMMARY,
            'message': message,
        })

    def render_error(self, message: str) -> None:
        """Render error message (backward compatible)."""
        self.error(message)
