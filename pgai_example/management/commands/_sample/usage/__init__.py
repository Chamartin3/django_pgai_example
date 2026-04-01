"""Usage command tree.

Three groups:
- `api/`       - one plugin API per command (single variant)
- `compare/models/` - cross-vectorizer comparisons (same query, all variants)
- `compare/strategies/` - strategy comparisons (one variant, different knobs)
"""
from .api import annotate, filter, find, rank
from .compare import demo, resultsCommand, timeCommand
from .compare.strategies import rankByCommand, thresholdCommand

__all__ = [
    "annotate",
    "filter",
    "find",
    "rank",
    "demo",
    "resultsCommand",
    "timeCommand",
    "rankByCommand",
    "thresholdCommand",
]
