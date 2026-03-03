"""Eval command dispatcher setup."""

# Import command instances for dispatcher
from .cutoff import cutoffCommand
from .ranking import rankingCommand

__all__ = [
    "rankingCommand",
    "cutoffCommand",
]
