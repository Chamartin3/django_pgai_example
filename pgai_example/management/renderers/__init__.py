"""CLI rendering components for management commands.

Usage:
    from pgai_example.management.renderers import RendererRegistry

    registry = RendererRegistry()
    registry.search.print(data)
    registry.message.error("Error message")
"""

from .base import CLIComponent
from .components import (
    AnnotateRenderer,
    CompareModelsRenderer,
    CompareTimingRenderer,
    EvalRenderer,
    ListRenderer,
    MessageRenderer,
    RankRenderer,
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
    'AnnotateRenderer',
    'CompareModelsRenderer',
    'CompareTimingRenderer',
    'EvalRenderer',
    'ListRenderer',
    'MessageRenderer',
    'RankRenderer',
    'SearchRenderer',
    'SeedRenderer',
]
