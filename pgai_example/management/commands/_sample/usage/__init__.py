"""Test command dispatcher setup."""

# Import command classes for dispatcher
from .eval.ranking import rankingCommand
from .filter import filter
from .search import search

__all__ = [
    "filter",
    "ranking",
    "search",
]
