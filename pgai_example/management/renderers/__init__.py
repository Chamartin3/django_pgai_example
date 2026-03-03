"""CLI rendering components for management commands.

Usage:
    from pgai_example.management.renderers import RendererRegistry

    registry = RendererRegistry()
    registry.search.print(data)
    registry.message.error("Error message")
"""

from .base import CLIComponent
from .components import (
    EvalRenderer,
    ListRenderer,
    MessageRenderer,
    SearchRenderer,
    SeedRenderer,
)
from .registry import (
    CLIComponentRegistry,
    CLIRenderer,
    RendererRegistry,
    SampleRendererRegistry,
)

__all__ = [
    'SampleRendererRegistry',
    'RendererRegistry',
    'CLIComponentRegistry',
    'CLIRenderer',
    'CLIComponent',
    'EvalRenderer',
    'ListRenderer',
    'MessageRenderer',
    'SearchRenderer',
    'SeedRenderer',
]
