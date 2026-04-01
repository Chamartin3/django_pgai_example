"""CLI rendering components.

Each component extends CLIComponent and follows the pattern:
    print(data) -> render(parsed) -> _parse(data)
"""
from .annotate import AnnotateRenderer
from .compare_models import CompareModelsRenderer
from .compare_timing import CompareTimingRenderer
from .eval import EvalRenderer
from .list import ListRenderer
from .message import MessageRenderer
from .rank import RankRenderer
from .search import SearchRenderer
from .seed import SeedRenderer

__all__ = [
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
