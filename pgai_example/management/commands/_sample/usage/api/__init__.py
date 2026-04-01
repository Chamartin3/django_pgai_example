"""Single-API demos.

Each command here demonstrates ONE distinct pgai plugin API entry point.
"""
from .annotate import annotate
from .filter import filter
from .find import find
from .rank import rank

__all__ = [
    "annotate",
    "filter",
    "find",
    "rank",
]
