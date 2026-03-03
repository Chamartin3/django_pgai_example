"""Abstract base class for CLI rendering components.

Call Structure:
    print(data) -> _parse(data) -> render(parsed) -> console output
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from rich.console import Console, RenderableType

TInput = TypeVar('TInput')
TParsed = TypeVar('TParsed')


class CLIComponent(ABC, Generic[TInput, TParsed]):
    """Abstract base class for CLI rendering components.

    Subclasses must implement render() and define component_name/component_key.
    """
    component_name: str = ''
    component_key: str = ''

    def __init__(self, console: Console | None = None, **kwargs):
        """Initialize component with console and optional config."""
        self.console = console if console else Console(color_system='256')
        self._config = kwargs

    def _parse(self, data: TInput) -> TParsed:
        """Prepare data for rendering. Default returns data unchanged."""
        return data  # type: ignore

    @abstractmethod
    def render(self, data: TParsed) -> RenderableType:
        """Create Rich renderable from prepared data."""
        pass

    def print(self, data: TInput) -> None:
        """Main entry point: parse data, render, and print to console."""
        parsed = self._parse(data)
        rendered = self.render(parsed)
        self.console.print(rendered)
