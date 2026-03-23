"""Test command dispatcher setup."""

# Import command classes for dispatcher
from .annotate import annotate
from .eval.ranking import rankingCommand
from .filter import filter
from .rank import rank
from .search import search
from .stats import stats

__all__ = [
    "annotate",
    "filter",
    "rank",
    "rankingCommand",
    "search",
    "stats",
]
