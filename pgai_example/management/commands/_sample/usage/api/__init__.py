"""Single-API demos.

Each command here demonstrates ONE distinct pgai plugin API entry point.
"""
from .annotate import annotate
from .filter import filter
from .find import find
from .multi_rank import multi_rank

__all__ = [
    "annotate",
    "filter",
    "find",
    "multi_rank",
]
